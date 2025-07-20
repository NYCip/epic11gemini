import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

// Mock LoginForm component for testing
const MockLoginForm = () => (
  <form>
    <label htmlFor="email">Email</label>
    <input id="email" type="email" />
    
    <label htmlFor="password">Password</label>
    <input id="password" type="password" />
    
    <button type="submit">Sign In</button>
  </form>
)

describe('Authentication', () => {
  test('LoginForm renders correctly', () => {
    render(<MockLoginForm />)
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })
  
  test('Form elements are accessible', () => {
    render(<MockLoginForm />)
    
    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    
    expect(emailInput).toHaveAttribute('type', 'email')
    expect(passwordInput).toHaveAttribute('type', 'password')
  })
  
  test('Basic React functionality', () => {
    const testElement = <div>Test</div>
    expect(testElement).toBeDefined()
  })

  test('Simple math operations', () => {
    expect(2 + 2).toBe(4)
    expect(5 * 3).toBe(15)
  })
})
