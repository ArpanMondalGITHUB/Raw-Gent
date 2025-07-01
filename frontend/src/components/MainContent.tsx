import {
  ChevronDown,
  GitBranch,
  ArrowRight,
  Play,
  Lightbulb,
  Plus,
  Check,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Textarea } from "../components/ui/textarea";
import { useEffect, useState } from "react";
import { installGithubApp } from "../services/github";
import { fetchbranch, fetchInstallRepos } from "../services/github_api";

export function MainContent() {
  const [selectedbranch, setSelectedbranch] = useState("(empty repo)");
  const [selectedRepo, setSelectedRepo] = useState<RepoType | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [pending, setPending] = useState(false);
  const [repos, setRepos] = useState([]);
  const [branches, setBranches] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [hasInitialized, setHasInitialized] = useState(false);

  const handleinstallGithubApp = () => {
    installGithubApp();
  };

  const handleRepoSelect = async(repo) => {
    setSelectedRepo(repo);
    setShowDropdown(false);
    try {
      const branchresponse = await fetchbranch(repo.name);
      const branchesdata = branchresponse.Branches || [];
      setBranches(branchesdata);

      if (branchesdata.length > 0) {
        setSelectedbranch(branchesdata[0].name);
      } else {
        setSelectedbranch("(empty repo)");
      }
    } catch (error) {
      console.error("Failed to fetch branches", error);
      setBranches([]);
      setSelectedbranch("(empty repo)");
    }
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
        console.log("📦 Repo Data:", data);
        const repositories = data.repositories || [];
        setRepos(repositories);
        setHasInitialized(true);

        // Auto-select the first repository
        if (repositories.length > 0) {
          const firstrepo = repositories[0];
          setSelectedRepo(firstrepo);

          const branchresponse = await fetchbranch(firstrepo.name);
          const branchesdata = branchresponse.Branches || [];
          setBranches(branchesdata);

          if (branchesdata.length > 0) {
            setSelectedbranch(branchesdata[0].name);
          }
        }
      } catch (error) {
        console.error("Failed to fetch repos", error);
        setRepos([]);
        setHasInitialized(true);
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
          <div className="mb-8">
            <div className="bg-[#1a1a1a] border border-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                {/* Repository Section */}
                <div className="flex items-center gap-2 flex-1 mr-4">
                  <GitBranch className="w-5 h-5 text-gray-500" />

                  {/* Repository Selection Logic */}
                  {!hasInitialized ? (
                    // Initial state - Add Repository button
                    <Button
                      variant="ghost"
                      className="text-gray-400 justify-between w-48"
                      onClick={handleinstallGithubApp}
                      disabled={pending}
                    >
                      {pending ? (
                        <>
                          <span className="flex items-center gap-2">
                            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                            Loading...
                          </span>
                        </>
                      ) : (
                        <>
                          Add Repository
                          <Plus className="w-4 h-4" />
                        </>
                      )}
                    </Button>
                  ) : selectedRepo ? (
                    // Selected repository with dropdown
                    <div className="relative">
                      <Button
                        variant="ghost"
                        className="text-gray-300 justify-between w-64 hover:bg-gray-800"
                        onClick={() => setShowDropdown(!showDropdown)}
                      >
                        <div className="flex items-center gap-2">
                          <Check className="w-4 h-4 text-green-500" />
                          <span className="truncate">
                            {selectedRepo.full_name}
                          </span>
                        </div>
                        <ChevronDown
                          className={`w-4 h-4 transition-transform ${
                            showDropdown ? "rotate-180" : ""
                          }`}
                        />
                      </Button>

                      {/* Repository Dropdown */}
                      {showDropdown && (
                        <div className="absolute top-full left-0 right-0 mt-2 bg-gray-800 border border-gray-600 rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto">
                          {repos.length > 0 ? (
                            <div className="py-2">
                              {/* Other repositories */}
                              {repos
                                .filter((repo) => repo.id !== selectedRepo.id)
                                .map((repo) => (
                                  <button
                                    key={repo.id}
                                    onClick={() => handleRepoSelect(repo)}
                                    className="w-full text-left px-4 py-3 text-gray-300 hover:bg-gray-700 transition-colors"
                                  >
                                    <div className="font-medium">
                                      {repo.full_name}
                                    </div>
                                    <div className="text-sm text-gray-500">
                                      {repo.name}
                                    </div>
                                  </button>
                                ))}

                              {/* Add more repositories button */}
                              <div className="border-t border-gray-700 mt-2 pt-2">
                                <button
                                  onClick={handleinstallGithubApp}
                                  className="w-full text-left px-4 py-3 text-blue-400 hover:bg-gray-700 transition-colors flex items-center gap-2"
                                >
                                  <Plus className="w-4 h-4" />
                                  Add more repositories
                                </button>
                              </div>
                            </div>
                          ) : (
                            <div className="p-4 text-gray-500 text-center">
                              No other repositories found
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ) : (
                    // No repos available
                    <Button
                      variant="ghost"
                      className="text-gray-400 justify-between w-48"
                      onClick={handleinstallGithubApp}
                    >
                      No repositories found
                      <Plus className="w-4 h-4" />
                    </Button>
                  )}
                </div>

                {/* Branch Section */}
                <div className="flex items-center gap-2">
                  <GitBranch className="w-5 h-5 text-gray-500" />

                  {branches.length > 0 ? (
                    <select
                      value={selectedbranch}
                      onChange={(e) => setSelectedbranch(e.target.value)}
                      className="bg-gray-800 text-white px-4 py-2 rounded w-48"
                    >
                      {branches.map((branch) => (
                        <option key={branch.name} value={branch.name}>
                          {branch.name}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <Button
                      variant="ghost"
                      className="text-gray-400 justify-between w-48"
                      disabled
                    >
                      {selectedbranch}
                      <ChevronDown className="w-4 h-4" />
                    </Button>
                  )}
                </div>

                {/* <div className="flex items-center gap-2">
                  <GitBranch className="w-5 h-5 text-gray-500" />
                  <Button
                    variant="ghost"
                    className="text-gray-400 justify-between w-48"
                    disabled={!selectedRepo}
                  >
                    {selectedbranch}
                    <ChevronDown className="w-4 h-4" />
                  </Button>
                </div> */}
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
