<script lang="ts">
  export let source = '';
  type Block = { type: 'h1' | 'h2' | 'h3' | 'p' | 'li' | 'code'; text: string };
  function parse(value: string): Block[] {
    const blocks: Block[] = [];
    let code = false;
    let codeLines: string[] = [];
    for (const line of value.replace(/^---[\s\S]*?---\s*/m, '').split('\n')) {
      if (line.startsWith('```')) { if (code) { blocks.push({ type: 'code', text: codeLines.join('\n') }); codeLines = []; } code = !code; continue; }
      if (code) { codeLines.push(line); continue; }
      if (line.startsWith('### ')) blocks.push({ type: 'h3', text: line.slice(4) });
      else if (line.startsWith('## ')) blocks.push({ type: 'h2', text: line.slice(3) });
      else if (line.startsWith('# ')) blocks.push({ type: 'h1', text: line.slice(2) });
      else if (/^[-*] /.test(line)) blocks.push({ type: 'li', text: line.slice(2) });
      else if (line.trim()) blocks.push({ type: 'p', text: line.trim() });
    }
    return blocks;
  }
  $: blocks = parse(source);
</script>
<div class="markdown">
  {#each blocks as block}
    {#if block.type === 'h1'}<h1>{block.text}</h1>
    {:else if block.type === 'h2'}<h2>{block.text}</h2>
    {:else if block.type === 'h3'}<h3>{block.text}</h3>
    {:else if block.type === 'li'}<div class="markdown-list"><span>•</span><p>{block.text}</p></div>
    {:else if block.type === 'code'}<pre><code>{block.text}</code></pre>
    {:else}<p>{block.text}</p>{/if}
  {/each}
</div>
