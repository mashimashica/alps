import { useEffect, useState } from "preact/hooks";
import type { AgentModelsResponse, AgentSelection } from "../../shared/types.ts";
import { useUi } from "../context.ts";
import { describeError } from "../api.ts";
import { Button } from "./button.tsx";
import { Field } from "./input.tsx";
import { Select } from "./select.tsx";
import { Icon } from "./icons.tsx";

/** Controlled per-launch choices. The caller keys this by agent and resets its choice on a switch. */
export function AgentSettings({
  agent,
  value,
  onChange,
  disabled = false,
}: {
  agent: string;
  value: AgentSelection;
  onChange: (selection: AgentSelection) => void;
  disabled?: boolean;
}) {
  const { client, t, language } = useUi();
  const [catalog, setCatalog] = useState<AgentModelsResponse | null>(null);
  const [failure, setFailure] = useState<unknown>(null);
  const [refresh, setRefresh] = useState(0);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let active = true;
    setLoading(true);
    setFailure(null);
    client
      .get<AgentModelsResponse>(
        `/api/agents/${encodeURIComponent(agent)}/models${refresh ? "?refresh=1" : ""}`,
      )
      .then(
        (answer) => {
          if (!active) return;
          setCatalog(answer);
          setLoading(false);
          const model = answer.models.find((m) => m.id === value.model);
          if (value.model && !model) onChange({});
          else if (value.effort && !model?.efforts.includes(value.effort))
            onChange({ model: value.model });
        },
        (error: unknown) => {
          if (active) {
            setFailure(error);
            setLoading(false);
          }
        },
      );
    return () => {
      active = false;
    };
  }, [agent, refresh]);
  if (catalog && !catalog.supported) return null;
  const selected = catalog?.models.find((model) => model.id === value.model);
  return (
    <div class="agent-settings" data-testid="agent-settings" aria-busy={loading}>
      <div class="agent-settings-fields">
        <Field label={t("agent.model")}>
          {(control) => (
            <Select
              id={control.id}
              labelledBy={control.labelId}
              value={value.model ?? ""}
              disabled={disabled || loading || !catalog}
              options={[
                { value: "", label: loading ? t("agent.loading") : t("agent.default") },
                ...(catalog?.models ?? []).map((model) => ({
                  value: model.id,
                  label: model.label,
                  hint: model.description,
                })),
              ]}
              onChange={(model) => onChange(model ? { model } : {})}
              testid="agent-model"
            />
          )}
        </Field>
        <Field label={t("agent.effort")}>
          {(control) => (
            <Select
              id={control.id}
              labelledBy={control.labelId}
              value={value.effort ?? ""}
              disabled={disabled || loading || !selected?.efforts.length}
              options={[
                {
                  value: "",
                  label:
                    selected && selected.efforts.length === 0
                      ? t("agent.noEffort")
                      : t("agent.default"),
                },
                ...(selected?.efforts ?? []).map((effort) => ({ value: effort, label: effort })),
              ]}
              onChange={(effort) => onChange({ model: value.model, ...(effort ? { effort } : {}) })}
              testid="agent-effort"
            />
          )}
        </Field>
      </div>
      <div class="agent-settings-status">
        <span class="faint small" role="status">
          {failure ? t("agent.loadFailed") : t("agent.liveChoices")}
        </span>
        <Button
          variant="ghost"
          size="sm"
          disabled={loading || disabled}
          onClick={() => setRefresh((n) => n + 1)}
        >
          <Icon name="refresh" size={13} />
          {t("agent.refresh")}
        </Button>
      </div>
      {failure !== null && (
        <p class="small agent-settings-error" role="alert">
          {describeError(failure, language)}
        </p>
      )}
    </div>
  );
}
