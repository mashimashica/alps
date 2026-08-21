<script lang="ts">export let tone: 'neutral' | 'info' | 'warning' | 'danger' | 'success' = 'neutral';</script>
<span class="badge {tone}"><slot /></span>
