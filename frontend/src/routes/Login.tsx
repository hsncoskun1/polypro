/**
 * Login page — v1.0.5
 */
import React, { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import type { LoginPayload } from '../hooks/useAuth'

interface Props {
  onLogin: (payload: LoginPayload) => void
}

export default function Login({ onLogin }: Props) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({ detail: 'Login failed' }))
        setError(data.detail ?? 'Login failed')
        setLoading(false)
        return
      }
      const payload = (await res.json()) as LoginPayload
      onLogin(payload)
      navigate(payload.role === 'admin' ? '/admin' : '/user')
    } catch (err) {
      setError('Network error. Please try again.')
      setLoading(false)
    }
  }

  return (
    <div className="login-page" data-testid="login-page">
      <h1>POLYPRO Login</h1>
      <form onSubmit={handleSubmit} className="login-form">
        <div className="form-field">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
            data-testid="login-email"
          />
        </div>
        <div className="form-field">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            data-testid="login-password"
          />
        </div>
        {error && (
          <div className="login-error" role="alert" data-testid="login-error">
            {error}
          </div>
        )}
        <button type="submit" disabled={loading} data-testid="login-submit">
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
      </form>
    </div>
  )
}
