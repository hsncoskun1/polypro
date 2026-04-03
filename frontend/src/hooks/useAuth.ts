/**
 * useAuth — session token management — v1.0.5
 */
import { useState, useCallback } from 'react'

const SESSION_TOKEN_KEY = 'polypro_session_token'
const USER_ID_KEY = 'polypro_user_id'
const USER_EMAIL_KEY = 'polypro_user_email'
const USER_ROLE_KEY = 'polypro_user_role'

export interface AuthState {
  sessionToken: string | null
  userId: string | null
  email: string | null
  role: string | null
  isAuthenticated: boolean
}

export interface LoginPayload {
  session_token: string
  user_id: string
  email: string
  role: string
}

export function useAuth() {
  const [sessionToken, setSessionToken] = useState<string | null>(
    () => sessionStorage.getItem(SESSION_TOKEN_KEY)
  )
  const [userId, setUserId] = useState<string | null>(
    () => sessionStorage.getItem(USER_ID_KEY)
  )
  const [email, setEmail] = useState<string | null>(
    () => sessionStorage.getItem(USER_EMAIL_KEY)
  )
  const [role, setRole] = useState<string | null>(
    () => sessionStorage.getItem(USER_ROLE_KEY)
  )

  const storeSession = useCallback((payload: LoginPayload) => {
    sessionStorage.setItem(SESSION_TOKEN_KEY, payload.session_token)
    sessionStorage.setItem(USER_ID_KEY, payload.user_id)
    sessionStorage.setItem(USER_EMAIL_KEY, payload.email)
    sessionStorage.setItem(USER_ROLE_KEY, payload.role)
    setSessionToken(payload.session_token)
    setUserId(payload.user_id)
    setEmail(payload.email)
    setRole(payload.role)
  }, [])

  const clearSession = useCallback(() => {
    sessionStorage.removeItem(SESSION_TOKEN_KEY)
    sessionStorage.removeItem(USER_ID_KEY)
    sessionStorage.removeItem(USER_EMAIL_KEY)
    sessionStorage.removeItem(USER_ROLE_KEY)
    setSessionToken(null)
    setUserId(null)
    setEmail(null)
    setRole(null)
  }, [])

  return {
    sessionToken,
    userId,
    email,
    role,
    isAuthenticated: sessionToken !== null,
    storeSession,
    clearSession,
  }
}
