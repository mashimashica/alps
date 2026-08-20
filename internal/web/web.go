package web

import "embed"

// Files contains the production-independent experimental web client.
//
//go:embed static/*
var Files embed.FS
