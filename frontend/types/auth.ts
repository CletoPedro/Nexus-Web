export interface CurrentUser {
  id: string;
  email: string;
  must_change_password: boolean;
  created_at: string | null;
}
