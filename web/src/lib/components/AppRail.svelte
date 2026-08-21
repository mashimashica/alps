<script lang="ts">
  import { page } from '$app/stores';
  const links = [
    { href: '/atlas', label: 'Atlas', icon: '◉' },
    { href: '/runs', label: 'Runs', icon: '▦' },
    { href: '/library', label: 'Library', icon: '◇' },
    { href: '/analysis', label: 'Analysis', icon: '⌁' }
  ];
</script>
<aside class="rail glass" aria-label="Primary navigation">
  <a class="brand" href="/atlas" aria-label="ALPS"><img src="/assets/icon.svg" alt="" /></a>
  {#each links as link}
    <a class:active={$page.url.pathname.startsWith(link.href)} class="nav-item" href={link.href} aria-label={link.label} title={link.label}><span aria-hidden="true">{link.icon}</span></a>
  {/each}
</aside>
