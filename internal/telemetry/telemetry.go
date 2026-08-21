package telemetry

import (
	"context"
	"errors"
	"os"
	"strings"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetrichttp"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
	"go.opentelemetry.io/otel/metric"
	"go.opentelemetry.io/otel/propagation"
	sdkmetric "go.opentelemetry.io/otel/sdk/metric"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	"go.opentelemetry.io/otel/trace"
)

type Runtime struct {
	Tracer            trace.Tracer
	Meter             metric.Meter
	HTTPRequests      metric.Int64Counter
	Commands          metric.Int64Counter
	CommandDuration   metric.Float64Histogram
	OutboxExports     metric.Int64Counter
	shutdownFunctions []func(context.Context) error
}

func Setup(ctx context.Context, serviceName string) (*Runtime, error) {
	resourceValue, err := resource.New(ctx, resource.WithAttributes(
		attribute.String("service.name", serviceName),
		attribute.String("service.version", "v0"),
		attribute.String("deployment.environment", "local"),
	))
	if err != nil {
		return nil, err
	}

	traceOptions := []sdktrace.TracerProviderOption{sdktrace.WithResource(resourceValue)}
	metricOptions := []sdkmetric.Option{sdkmetric.WithResource(resourceValue)}
	var shutdowns []func(context.Context) error

	if exporterEnabled("OTEL_TRACES_EXPORTER") {
		exporter, exportErr := otlptracehttp.New(ctx)
		if exportErr != nil {
			return nil, exportErr
		}
		traceOptions = append(traceOptions, sdktrace.WithBatcher(exporter))
	}
	tracerProvider := sdktrace.NewTracerProvider(traceOptions...)
	shutdowns = append(shutdowns, tracerProvider.Shutdown)

	if exporterEnabled("OTEL_METRICS_EXPORTER") {
		exporter, exportErr := otlpmetrichttp.New(ctx)
		if exportErr != nil {
			return nil, exportErr
		}
		reader := sdkmetric.NewPeriodicReader(exporter, sdkmetric.WithInterval(30*time.Second))
		metricOptions = append(metricOptions, sdkmetric.WithReader(reader))
	}
	meterProvider := sdkmetric.NewMeterProvider(metricOptions...)
	shutdowns = append(shutdowns, meterProvider.Shutdown)

	otel.SetTracerProvider(tracerProvider)
	otel.SetMeterProvider(meterProvider)
	otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(propagation.TraceContext{}, propagation.Baggage{}))

	meter := meterProvider.Meter("alps.local-runtime")
	httpRequests, _ := meter.Int64Counter("alps.http.requests")
	commands, _ := meter.Int64Counter("alps.commands")
	commandDuration, _ := meter.Float64Histogram("alps.command.duration", metric.WithUnit("ms"))
	outboxExports, _ := meter.Int64Counter("alps.telemetry.outbox.exports")

	return &Runtime{
		Tracer:            tracerProvider.Tracer("alps.local-runtime"),
		Meter:             meter,
		HTTPRequests:      httpRequests,
		Commands:          commands,
		CommandDuration:   commandDuration,
		OutboxExports:     outboxExports,
		shutdownFunctions: shutdowns,
	}, nil
}

func (runtime *Runtime) Shutdown(ctx context.Context) error {
	if runtime == nil {
		return nil
	}
	var failures []error
	for index := len(runtime.shutdownFunctions) - 1; index >= 0; index-- {
		if err := runtime.shutdownFunctions[index](ctx); err != nil {
			failures = append(failures, err)
		}
	}
	return errors.Join(failures...)
}

func exporterEnabled(selector string) bool {
	value := strings.TrimSpace(strings.ToLower(os.Getenv(selector)))
	if value == "none" {
		return false
	}
	if value == "otlp" {
		return true
	}
	return os.Getenv("OTEL_EXPORTER_OTLP_ENDPOINT") != "" ||
		os.Getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT") != "" ||
		os.Getenv("OTEL_EXPORTER_OTLP_METRICS_ENDPOINT") != ""
}
