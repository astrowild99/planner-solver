{{/*
Expand the name of the chart.
*/}}
{{- define "planner-solver.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "planner-solver.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "planner-solver.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels - these ensure Portainer groups all resources together
*/}}
{{- define "planner-solver.labels" -}}
helm.sh/chart: {{ include "planner-solver.chart" . }}
{{ include "planner-solver.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels - used to group all resources under one application
*/}}
{{- define "planner-solver.selectorLabels" -}}
app.kubernetes.io/name: {{ include "planner-solver.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
MongoDB specific labels
*/}}
{{- define "planner-solver.mongodb.labels" -}}
{{ include "planner-solver.labels" . }}
app.kubernetes.io/component: database
{{- end }}

{{/*
MongoDB selector labels
*/}}
{{- define "planner-solver.mongodb.selectorLabels" -}}
{{ include "planner-solver.selectorLabels" . }}
app.kubernetes.io/component: database
{{- end }}

{{/*
RabbitMQ specific labels
*/}}
{{- define "planner-solver.rabbitmq.labels" -}}
{{ include "planner-solver.labels" . }}
app.kubernetes.io/component: messaging
{{- end }}

{{/*
RabbitMQ selector labels
*/}}
{{- define "planner-solver.rabbitmq.selectorLabels" -}}
{{ include "planner-solver.selectorLabels" . }}
app.kubernetes.io/component: messaging
{{- end }}

{{/*
Planner Solver API labels
*/}}
{{- define "planner-solver.api.labels" -}}
{{ include "planner-solver.labels" . }}
app.kubernetes.io/component: api
{{- end }}

{{/*
Planner Solver API selector labels
*/}}
{{- define "planner-solver.api.selectorLabels" -}}
{{ include "planner-solver.selectorLabels" . }}
app.kubernetes.io/component: api
{{- end }}

{{/*
Planner Solver Runner labels
*/}}
{{- define "planner-solver.runner.labels" -}}
{{ include "planner-solver.labels" . }}
app.kubernetes.io/component: worker
{{- end }}

{{/*
Planner Solver Runner selector labels
*/}}
{{- define "planner-solver.runner.selectorLabels" -}}
{{ include "planner-solver.selectorLabels" . }}
app.kubernetes.io/component: worker
{{- end }}
