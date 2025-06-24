import {
  ChevronDown,
  GitBranch,
  ArrowRight,
  Play,
  Lightbulb,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Textarea } from "../components/ui/textarea";
import { useEffect, useState } from "react";
import { installGithubApp } from "../services/github";
import { fetchInstallRepos } from "../services/github_api";

export function MainContent() {
  const [selectedbranch, setSelectedbranch] = useState("(empty repo)");
  const [selectedRepo, setSelectedRepo] = useState("Add Repository");
  const [inputValue, setInputValue] = useState("");
  const [pending, setPending] = useState(false);
  const [repos, setRepos] = useState([]);

  const handleinstallGithubApp = () => {
    installGithubApp();
  };

  useEffect(() => {
  const params = new URLSearchParams(window.location.search);
  const hasInstall = params.get("installation_id");

  if (hasInstall) {
    window.history.replaceState({}, document.title, window.location.pathname);
  }
    const loadrepos = async () => {
      setPending(true);
      try {
        const data = await fetchInstallRepos();
        setRepos(data.repositories || []);
      } catch (error) {
        console.error("Failed to fetch repos", error);
        setRepos([]);
      } finally {
        setPending(false);
      }
    };
    loadrepos();
  }, []);

  return (
    <div className="flex-1 flex flex-col  bg-[#1a1a1a]">
      {/* Header */}
      <div className="p-6 border-b border-gray-800">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-white mb-2">
            Raw-Gent: an async development agent.
          </h1>
          <p className="text-gray-400 text-lg">
            Raw-Gent tackles bugs, small feature requests and other software
            engineering tasks, with direct export to GitHub.
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6">
        <div className="max-w-4xl mx-auto">
          {/* Repository Selection */}
          <div className="mb-8">
            <div className="bg-[#1a1a1a] border border-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <GitBranch className="w-5 h-5 text-gray-500" />
                  <Button
                    variant="ghost"
                    className="text-gray-400 justify-between w-48"
                    onClick={handleinstallGithubApp}
                  >
                    {selectedRepo}
                    <ChevronDown className="w-4 h-4" />
                    {repos.length > 0 ? (
                      <select
                        value={selectedRepo}
                        onChange={(e) => setSelectedRepo(e.target.value)}
                        className="bg-gray-800 text-white px-4 py-2 rounded"
                      >
                        <option disabled value="Add Repository">
                          Select a Repository
                        </option>
                        {(repos || []).map((repo) => (
                          <option key={repo.id} value={repo.name}>
                            {repo.full_name}
                          </option>
                        ))}
                      </select>
                    ) : ( null
                    )}
                  </Button>
                </div>
                <div className="flex items-center gap-2">
                  <GitBranch className="w-5 h-5 text-gray-500" />
                  <Button
                    variant="ghost"
                    className="text-gray-400  justify-between w-48"
                  >
                    {selectedbranch}
                    <ChevronDown className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <div className="relative">
                <Textarea
                  placeholder="Help me fix this error ..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  className="min-h-[120px] bg-transparent border-none text-gray-300 placeholder-gray-600 resize-none text-lg p-0"
                />
                <Button
                  className="absolute bottom-4 right-4 bg-gray-700 hover:bg-gray-600 text-gray-300"
                  size="sm"
                >
                  Give me a plan
                  <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 justify-center">
            <Button
              variant="ghost"
              className="flex items-center gap-2 text-purple-400 hover:text-purple-300 border border-purple-500/20 hover:border-purple-500/40"
            >
              <Play className="w-4 h-4" />
              How it works
            </Button>
            <Button
              variant="ghost"
              className="flex items-center gap-2 text-purple-400 hover:text-purple-300 border border-purple-500/20 hover:border-purple-500/40"
            >
              <Lightbulb className="w-4 h-4" />
              Need inspiration?
            </Button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-6 border-t border-gray-800">
        <div className="max-w-4xl mx-auto">
          <div className="flex justify-center gap-6 text-sm text-gray-500">
            <a href="#" className="hover:text-gray-400">
              Terms
            </a>
            <a href="#" className="hover:text-gray-400">
              Open source licenses
            </a>
            <a href="#" className="hover:text-gray-400">
              Use code with caution
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
