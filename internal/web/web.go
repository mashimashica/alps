package web

import "embed"

// Files contains the built ALPS Local Runtime web application.
//
//go:embed all:static
var Files embed.FS
