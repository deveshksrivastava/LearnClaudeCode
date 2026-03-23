import client from './client';

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
}

export async function registerUser(payload: RegisterPayload) {
  const { data } = await client.post('/register', payload);
  return data as { id: number; name: string; email: string };
}
