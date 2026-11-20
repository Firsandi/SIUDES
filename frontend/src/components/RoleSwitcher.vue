<script setup>
import { useRole } from '../composables/useRole'

const { roles, activeRole, setRole } = useRole()
</script>

<template>
  <div
    class="inline-flex flex-wrap items-center gap-1.5 rounded-full bg-white p-1.5 shadow-sm"
    role="group"
    aria-label="Global Role Switcher"
  >
    <button
      v-for="role in roles"
      :key="role.code"
      type="button"
      class="rounded-full px-3.5 py-1.5 text-xs font-medium transition-all"
      :class="
        activeRole === role.code
          ? 'bg-ink text-white shadow-sm'
          : 'bg-transparent text-muted hover:bg-frame hover:text-ink'
      "
      @click="setRole(role.code)"
    >
      {{ role.code }}
    </button>
  </div>
</template>
