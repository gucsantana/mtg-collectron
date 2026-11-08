<template>
  <v-app-bar color="primary">
    <v-btn @click="$emit('back')">
      <v-icon icon="mdi-arrow-left" size="x-large" />
      <span class="ml-2">Back to Collection</span>
    </v-btn>
    <v-spacer />
    <span class="account_page_title">Account Management</span>
    <v-spacer />
    <v-btn icon="mdi-menu" aria-label="Open settings" @click="$emit('open-settings')" />
  </v-app-bar>
  <v-main class="account_page_main">
    <v-container class="account_page_content">
      <v-alert v-if="error" type="error" variant="tonal">{{ error }}</v-alert>
      <v-alert v-if="message" type="success" variant="tonal">{{ message }}</v-alert>

      <v-card class="account_panel">
        <v-card-title>Account Information</v-card-title>
        <v-card-text>
          <div class="account_detail">
            <span class="account_detail_label">Username</span>
            <span>{{ user?.username || 'Not available' }}</span>
          </div>
          <div class="account_detail">
            <span class="account_detail_label">Email</span>
            <span>{{ user?.email || 'Not available' }}</span>
          </div>
        </v-card-text>
      </v-card>

      <v-card class="account_panel">
        <v-card-title>Change Password</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="changePassword">
            <v-text-field v-model="currentPassword" label="Current password" type="password"
              autocomplete="current-password" required variant="outlined" />
            <v-text-field v-model="newPassword" label="New password" type="password" autocomplete="new-password"
              minlength="8" maxlength="72" required variant="outlined" />
            <v-text-field v-model="confirmNewPassword" label="Confirm new password" type="password"
              autocomplete="new-password" minlength="8" maxlength="72" required variant="outlined" />
            <v-btn type="submit" color="primary" :loading="processing === 'password'"
              :disabled="processing !== ''">
              Change Password
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>

      <v-card class="account_panel delete_account_panel">
        <v-card-title>Delete Account</v-card-title>
        <v-card-text>
          <p class="delete_account_warning">
            Permanently delete your account and its collection data. This action cannot be undone.
          </p>
          <v-form @submit.prevent="deleteAccount">
            <v-text-field v-model="deletePassword" label="Password" type="password" autocomplete="current-password"
              required variant="outlined" />
            <v-checkbox v-model="confirmDelete" color="error"
              label="I understand that deleting my account is permanent." />
            <v-btn type="submit" color="error" :loading="processing === 'delete'"
              :disabled="processing !== '' || !deletePassword || !confirmDelete">
              Delete Account
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </v-container>
  </v-main>
</template>

<script setup>
import { ref } from 'vue'
import { authFetch } from './authFetch.js'

const props = defineProps({
  user: { type: Object, required: true },
  userId: { type: [String, Number], required: true },
  csrfToken: { type: String, required: true },
})
const emit = defineEmits(['back', 'open-settings', 'password-changed', 'account-deleted'])

const currentPassword = ref('')
const newPassword = ref('')
const confirmNewPassword = ref('')
const deletePassword = ref('')
const confirmDelete = ref(false)
const processing = ref('')
const error = ref('')
const message = ref('')

async function getResponseError(response, fallback) {
  const body = await response.text()
  if (!body) return `${fallback} (HTTP ${response.status}).`

  try {
    const result = JSON.parse(body)
    return result.message || result.error || body
  } catch {
    return body
  }
}

async function getPasswordActionError(response, fallback) {
  const detail = await getResponseError(response, fallback)
  if ((response.status === 401 || response.status === 403) && !/csrf|security token/i.test(detail)) {
    return 'The password provided does not match our records.'
  }
  return detail
}

async function changePassword() {
  error.value = ''
  message.value = ''

  if (!currentPassword.value || !newPassword.value) {
    error.value = 'Enter your current password and a new password.'
    return
  }
  if (newPassword.value.length < 8 || newPassword.value.length > 72) {
    error.value = 'Your new password must be between 8 and 72 characters.'
    return
  }
  if (newPassword.value !== confirmNewPassword.value) {
    error.value = 'The new passwords do not match.'
    return
  }
  if (newPassword.value === currentPassword.value) {
    error.value = 'Choose a new password that is different from your current password.'
    return
  }
  if (!props.csrfToken) {
    error.value = 'The security token is unavailable. Refresh the page and try again.'
    return
  }

  processing.value = 'password'
  let passwordChanged = false
  let reauthenticated = false
  try {
    const response = await authFetch('/mtg-collectron/auth/change-password', {
      method: 'POST',
      credentials: 'include',
      suppressAuthenticationRedirect: true,
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': props.csrfToken,
      },
      body: JSON.stringify({
        userId: props.userId,
        currentPassword: currentPassword.value,
        desiredPassword: newPassword.value,
      }),
    })
    if (!response.ok) {
      throw new Error(await getPasswordActionError(response, 'Unable to change your password'))
    }
    passwordChanged = true

    const csrfResponse = await authFetch('/mtg-collectron/auth/csrf', {
      method: 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    })
    if (!csrfResponse.ok) {
      throw new Error(`Unable to retrieve a CSRF token (HTTP ${csrfResponse.status}).`)
    }
    const csrfResult = await csrfResponse.json()
    if (!csrfResult.token) {
      throw new Error('The server did not provide a CSRF token.')
    }

    const loginResponse = await authFetch('/mtg-collectron/auth/login', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfResult.token,
      },
      body: JSON.stringify({
        username: props.user.username,
        password: newPassword.value,
      }),
    })
    if (!loginResponse.ok) {
      throw new Error(await getResponseError(loginResponse, 'Unable to sign in with your new password'))
    }
    const loginResult = await loginResponse.json()
    reauthenticated = true

    const refreshedCsrfResponse = await authFetch('/mtg-collectron/auth/csrf', {
      method: 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    })
    if (!refreshedCsrfResponse.ok) {
      throw new Error(`Unable to refresh the CSRF token (HTTP ${refreshedCsrfResponse.status}).`)
    }
    const refreshedCsrfResult = await refreshedCsrfResponse.json()
    if (!refreshedCsrfResult.token) {
      throw new Error('The server did not provide a refreshed CSRF token.')
    }

    emit('password-changed', {
      user: loginResult.user ?? loginResult,
      csrfToken: refreshedCsrfResult.token,
    })
  } catch (requestError) {
    const detail = requestError instanceof Error ? requestError.message : 'Please try again.'
    error.value = passwordChanged
      ? reauthenticated
        ? `Your password was changed and you were signed in, but the security token could not be refreshed: ${detail}`
        : `Your password was changed, but automatic sign-in failed: ${detail}`
      : detail
  } finally {
    processing.value = ''
  }
}

async function deleteAccount() {
  error.value = ''
  message.value = ''

  if (!deletePassword.value || !confirmDelete.value) {
    error.value = 'Enter your password and confirm that you understand this action is permanent.'
    return
  }
  if (!props.csrfToken) {
    error.value = 'The security token is unavailable. Refresh the page and try again.'
    return
  }

  processing.value = 'delete'
  try {
    const response = await authFetch('/mtg-collectron/auth/delete-account', {
      method: 'POST',
      credentials: 'include',
      suppressAuthenticationRedirect: true,
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': props.csrfToken,
      },
      body: JSON.stringify({
        userId: props.userId,
        password: deletePassword.value,
      }),
    })
    if (!response.ok) {
      throw new Error(await getPasswordActionError(response, 'Unable to delete your account'))
    }

    emit('account-deleted')
  } catch (requestError) {
    error.value = requestError instanceof Error
      ? requestError.message
      : 'Unable to delete your account. Please try again.'
  } finally {
    processing.value = ''
  }
}
</script>

<style scoped>
.account_page_main {
  margin: 0 auto;
  width: 100%;
  max-width: 760px;
}

.account_page_content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-top: 30px;
  padding-bottom: 40px;
}

.account_panel {
  width: 100%;
  padding: 8px 20px;
}

.account_detail {
  display: flex;
  gap: 12px;
  margin: 8px 0;
  overflow-wrap: anywhere;
}

.account_detail_label {
  min-width: 90px;
  font-weight: 600;
}

.delete_account_panel {
  border: 1px solid rgb(var(--v-theme-error));
}

.delete_account_warning {
  margin-bottom: 16px;
  color: rgb(var(--v-theme-error));
  font-weight: 500;
}

.account_page_title {
  font-size: 1.2rem;
  font-weight: 500;
}

@media (max-width: 600px) {
  .account_page_title {
    display: none;
  }

  .account_page_content {
    padding: 16px 8px 24px;
  }

  .account_panel {
    padding: 8px;
  }
}
</style>
