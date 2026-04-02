import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Home from '../routes/Home'
import UserPanel from '../routes/UserPanel'
import AdminPanel from '../routes/AdminPanel'

test('Home renders POLYPRO title', () => {
  render(<MemoryRouter><Home /></MemoryRouter>)
  expect(screen.getByText('POLYPRO')).toBeInTheDocument()
})

test('UserPanel renders', () => {
  render(<MemoryRouter><UserPanel /></MemoryRouter>)
  expect(screen.getByText('User Panel')).toBeInTheDocument()
})

test('AdminPanel renders', () => {
  render(<MemoryRouter><AdminPanel /></MemoryRouter>)
  expect(screen.getByText('Admin Panel')).toBeInTheDocument()
})
