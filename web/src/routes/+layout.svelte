<script lang="ts">
  import '../app.css';
  import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query';
  import { onMount } from 'svelte';
  import AppShell from '$lib/components/AppShell.svelte';
  import { connectRealtime } from '$lib/realtime';
  const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 8_000, refetchOnWindowFocus: false } } });
  onMount(() => connectRealtime(queryClient));
</script>
<QueryClientProvider client={queryClient}><AppShell><slot /></AppShell></QueryClientProvider>
