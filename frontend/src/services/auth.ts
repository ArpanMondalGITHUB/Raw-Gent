import { LOGIN_URL } from "../config/runtime";

export const loginWithGitHub = () => {
  window.location.href = LOGIN_URL;
};

