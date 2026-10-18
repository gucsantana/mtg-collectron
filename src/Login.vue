<template>
  <v-app>
    <main class="login_page">
      <v-card class="login_box" elevation="8">
        <img class="login_logo" src="@/assets/collectron-title-logo.png" alt="MTG Collectron">
        <h1 class="login_title">{{ isRegistering ? 'Create an Account' : 'Welcome Back!' }}</h1>
        <br />

        <v-alert v-if="visibleError" type="error" variant="tonal" class="login_alert">
          {{ visibleError }}
        </v-alert>

        <v-form @submit.prevent="submitForm">
          <v-text-field v-model="username" label="Username" autocomplete="username" minLength="6" maxlength="100"
            :rules="usernameRules" required variant="outlined" />
          <v-text-field v-if="isRegistering" v-model="email" label="Email" type="email" autocomplete="email"
            maxlength="254" required variant="outlined" />
          <v-text-field v-model="password" label="Password" type="password" minLength="8" maxlength="72"
            :autocomplete="isRegistering ? 'new-password' : 'current-password'" required variant="outlined" />
          <v-text-field v-if="isRegistering" v-model="passwordConfirmation" label="Confirm password" type="password"
            autocomplete="new-password" required variant="outlined" />

          <v-row>
            <v-col cols="3">
              <v-btn type="submit" color="primary" block :loading="submitting" :disabled="submitting">
                {{ isRegistering ? 'Register' : 'Log In' }}
              </v-btn>
            </v-col>
            <v-spacer />
            <v-col cols="8">
              <v-btn id="change_login_mode" type="button" color="tertiary" block :disabled="submitting"
                @click="toggleMode">
                {{ isRegistering ? 'Already signed up? Log in' : 'New here? Create account' }}
              </v-btn>
            </v-col>
          </v-row>
        </v-form>

      </v-card>
    </main>
  </v-app>
</template>

<script setup>
import { computed, ref } from 'vue'

defineOptions({ name: 'UserLogin' })

const emit = defineEmits(['authenticated'])
const props = defineProps({
  initialError: {
    type: String,
    default: '',
  },
})

const isRegistering = ref(false)
const username = ref('')
const email = ref('')
const password = ref('')
const passwordConfirmation = ref('')
const submitting = ref(false)
const errorMessage = ref('')
const usernameRules = [
  value => !!value || 'Username is required.',
  value => /^[A-Za-z0-9_-]+$/.test(value) || 'Use only letters, numbers, hyphens, and underscores.',
  value => value.length >= 6 || 'Username must have 6 characters or more.',
]

const visibleError = computed(() => errorMessage.value || props.initialError)

function toggleMode() {
  isRegistering.value = !isRegistering.value
  errorMessage.value = ''
  password.value = ''
  passwordConfirmation.value = ''
}

async function submitForm() {
  if (isRegistering.value) {
    await createAccount()
  } else {
    await logIn()
  }
}

async function logIn() {
  submitting.value = true
  errorMessage.value = ''

  try {
    if (!username.value.trim() || !password.value) {
      throw new Error('Enter your username and password.')
    }
    // CSRF token is necessary to validade most auth methods
    const csrfCall = await fetch('/mtg-collectron/auth/csrf', {
      method: 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    })
    if (!csrfCall.ok) {
      throw new Error(result.message || 'Error during CSRF token call.')
    }
    const csrfCallResponse = await csrfCall.json()

    const response = await fetch('/mtg-collectron/auth/login', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfCallResponse['token']
      },
      body: JSON.stringify({ username: username.value.trim(), password: password.value }),
    })
    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.message || 'Unable to log in with those credentials.')
    }

    emit('authenticated', result.user ?? result)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Unable to log in. Please try again.'
  } finally {
    submitting.value = false
  }
}

async function createAccount() {
  submitting.value = true
  errorMessage.value = ''

  try {
    // Check the repeated password before contacting the server. This is only a usability check:
    // all validation must also happen on the backend because browser-side checks can be bypassed.
    if (!email.value.trim() || !username.value.trim() || !password.value) {
      throw new Error('Enter an email, username, and password.')
    }
    if (!/^[A-Za-z0-9_-]+$/.test(username.value)) {
      throw new Error('Username can contain only letters, numbers, hyphens, and underscores.')
    }
    if (password.value.length < 8) {
      throw new Error('Password must have at least 8 characters.')
    }
    if (password.value !== passwordConfirmation.value) {
      throw new Error('The passwords do not match.')
    }

    // Send only the fields needed to create an account. The raw password is sent over HTTPS so
    // the server can hash it; a password hash made in the browser would not replace secure
    // server-side hashing and must never be stored in localStorage or sent as the DB hash.
    const response = await fetch('/mtg-collectron/auth/register', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email.value.trim(),
        username: username.value.trim(),
        password: password.value,
      }),
    })
    const result = await response.json()

    // A successful registration is expected to create an authenticated server session and
    // return the public user record. The backend should hash the password, enforce the unique
    // email/username constraints, set an HttpOnly session cookie, and never return password_hash.
    // Keeping those responsibilities on the server prevents the client from choosing account
    // IDs, activation state, verification state, login timestamps, or stored password hashes.
    if (!response.ok) {
      throw new Error(result.message || 'Unable to create the account. Please check your details.')
    }

    // Only the returned public profile is passed to the app. Session credentials remain in the
    // browser-managed cookie and are included automatically by future same-origin API requests.
    emit('authenticated', result.user ?? result)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Unable to create the account. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.login_page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 24px;
  background: linear-gradient(145deg, #fff7f8, #f5f7fb);
}

.login_box {
  width: 100%;
  max-width: 440px;
  padding: 32px;
  border-radius: 16px;
  text-align: center;
}

.login_logo {
  width: 100%;
  max-width: 310px;
  margin: 0 auto 12px;
}

.login_title {
  font-family: Georgia, 'Times New Roman', Times, serif;
  font-size: 24px;
  font-weight: bold;
}

.login_subtitle {
  margin: 4px 0 24px;
  color: #666;
}

.login_alert {
  margin-bottom: 18px;
  text-align: left;
}

.mode_button {
  margin-top: 12px;
}

@media screen and (max-width: 480px) {
  .login_box {
    padding: 24px 18px;
  }
}
</style>
