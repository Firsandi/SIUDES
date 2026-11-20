<script setup>
import { useNavigation } from './composables/useNavigation'
import LandingView from './views/LandingView.vue'
import WorkspaceView from './views/WorkspaceView.vue'

const { currentRoute } = useNavigation()
</script>

<template>
  <LandingView v-if="currentRoute === 'landing'" />
  <WorkspaceView v-else />
</template>
