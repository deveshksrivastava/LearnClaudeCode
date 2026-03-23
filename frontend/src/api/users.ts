import client from './client';

export interface User {
  id: number;
  name: string;
  email: string;
}

export async function getUsers(q = ''): Promise<User[]> {
  const { data } = await client.get('/users', { params: q ? { q } : {} });
  return data as User[];
}

export async function updateUser(id: number, payload: { name: string; email: string }): Promise<User> {
  const { data } = await client.put(`/users/${id}`, payload);
  return data as User;
}

export async function deleteUser(id: number): Promise<void> {
  await client.delete(`/users/${id}`);
}
