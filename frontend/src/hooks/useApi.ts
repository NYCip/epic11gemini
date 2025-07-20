'use client'

import axios from 'axios'
import { useSession } from 'next-auth/react'

export const useApi = () => {
  const { data: session } = useSession()

  const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL,
    headers: {
      Authorization: `Bearer ${session?.accessToken}`,
    },
  })

  return api
}
