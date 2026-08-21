<script lang="ts">
  export let variant: 'primary' | 'secondary' | 'ghost' | 'danger' = 'secondary';
  export let type: 'button' | 'submit' = 'button';
  export let disabled = false;
</script>
<button {type} {disabled} class="button {variant}" on:click><slot /></button>
