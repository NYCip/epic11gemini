import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { LoginForm } from '../src/components/auth/LoginForm'
import { useRouter } from 'next/navigation'
import { signIn } from 'next-auth/react'

jest.mock('next/navigation')
jest.mock('next-auth/react')

describe('Authentication', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('LoginForm renders correctly', () => {
    render(<LoginForm />)
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  test('LoginForm validates required fields', async () => {
    render(<LoginForm />)
    
    const submitButton = screen.getByRole('button', { name: /sign in/i })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument()
      expect(screen.getByText(/password is required/i)).toBeInTheDocument()
    })
  })

  test('LoginForm submits with valid credentials', async () => {
    const mockRouter = { push: jest.fn() }
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    ;(signIn as jest.Mock).mockResolvedValue({ ok: true })
    
    render(<LoginForm />)
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'eip @iug.net' }
    })
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: '1234Abcd!' }
    })
    
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))
    
    await waitFor(() => {
      expect(signIn).toHaveBeenCalledWith('credentials', {
        email: 'eip @iug.net',
        password: '1234Abcd!',
        redirect: false
      })
      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard')
    })
  })

  test('AuthGuard redirects unauthenticated users', async () => {
    // Test implementation
  })
})
