import { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import axios from 'axios'

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }
        
        try {
          const response = await axios.post(
            `${process.env.NEXT_PUBLIC_API_URL}/control/auth/token`,
            new URLSearchParams({
              username: credentials.email,
              password: credentials.password
            }),
            {
              headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
              }
            }
          )
          
          if (response.data.access_token) {
            // Get user details
            const userResponse = await axios.get(
              `${process.env.NEXT_PUBLIC_API_URL}/control/users/me`,
              {
                headers: {
                  Authorization: `Bearer ${response.data.access_token}`
                }
              }
            )
            
            return {
              id: userResponse.data.id,
              email: userResponse.data.email,
              name: userResponse.data.full_name,
              role: userResponse.data.role,
              accessToken: response.data.access_token
            }
          }
          
          return null
        } catch (error) {
          return null
        }
      }
    })
  ],
  session: {
    strategy: 'jwt'
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
        token.email = user.email
        token.role = user.role
        token.accessToken = user.accessToken
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string
        session.user.email = token.email as string
        session.user.role = token.role as string
        session.accessToken = token.accessToken as string
      }
      return session
    }
  },
  pages: {
    signIn: '/auth/login',
    error: '/auth/error'
  }
}
