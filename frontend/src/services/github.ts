import { GITHUB_APP_INSTALL_URL } from "../config/runtime";

export const installGithubApp = () =>{
    window.location.href = GITHUB_APP_INSTALL_URL;
};
