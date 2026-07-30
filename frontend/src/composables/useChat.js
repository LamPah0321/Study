import { ref } from 'vue'

// Module-level reactive state — shared across every component that uses the composable.
const isOpen = ref(false)
const pendingQuestion = ref('')

export function useChatOpen() {
  function open(question = '') {
    if (question) pendingQuestion.value = question
    isOpen.value = true
  }

  function close() {
    isOpen.value = false
  }

  function toggle() {
    isOpen.value = !isOpen.value
  }

  function consumePendingQuestion() {
    const q = pendingQuestion.value
    pendingQuestion.value = ''
    return q
  }

  return {
    isOpen,
    open,
    close,
    toggle,
    pendingQuestion,
    consumePendingQuestion,
  }
}
