import { AppSidebar } from "../components/AppSidebar";
import { MainContent } from "../components/MainContent";
import { TopBar } from "../components/TopBar";

const Home = () => {
  return (
    <div className="min-h-screen flex bg-[#0a0a0a] relative">
      <AppSidebar />
      <MainContent />
      <TopBar />
    </div>
  );
};

export default Home;