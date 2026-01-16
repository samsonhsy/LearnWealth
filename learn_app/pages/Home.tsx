import { Bot, Gift, PlayCircle } from "lucide-react";

 export default function HomeView (props) {
    const { user, View, setView } = props;
    return (
    <div className="p-4 space-y-6 pb-24">
      <div className="flex items-center justify-between">
        <h2 className="text-xl lg:text-2xl font-bold">Your Progress</h2>
        <div className="flex gap-1">
          {user.interests.map(i => (
            <span key={i} className="text-[10px] bg-teal-50 text-teal-700 px-2 py-1 rounded-full border border-teal-100 uppercase tracking-tighter font-black">#{i.replace(' ', '')}</span>
          ))}
        </div>
      </div>

      <div className="bg-gradient-to-br from-teal-600 to-teal-800 rounded-3xl p-6 text-white shadow-xl relative overflow-hidden">
        <div className="relative z-10">
          <p className="text-teal-100 text-sm lg:text-base mb-1">K Dollar Balance</p>
          <h2 className="text-5xl font-black mb-4">{user.kDollars}</h2>
          <div className="flex gap-3">
             <div className="bg-white/20 px-3 py-1 rounded-lg text-xs lg:text-sm backdrop-blur-md">🔥 {user.streakDays} Day Streak</div>
             <div className="bg-white/20 px-3 py-1 rounded-lg text-xs lg:text-sm backdrop-blur-md">🏆 Level {user.level}</div>
          </div>
        </div>
        <Bot className="absolute -right-4 -bottom-4 opacity-10" size={120} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <button onClick={() => setView(View.LEARN)} className="bg-blue-600 p-6 rounded-3xl text-white shadow-lg shadow-blue-500/20 text-left">
           <PlayCircle className="mb-4" size={32} />
           <p className="font-bold text-lg lg:text-2xl leading-tight">Resume Lesson</p>
           <p className="text-xs lg:text-sm text-blue-100 mt-1">Budgeting Basics</p>
        </button>
        <button onClick={() => setView(View.REWARDS)} className="bg-purple-600 p-6 rounded-3xl text-white shadow-lg shadow-purple-500/20 text-left">
           <Gift className="mb-4" size={32} />
           <p className="font-bold text-lg lg:text-2xl leading-tight">My Rewards</p>
           <p className="text-xs lg:text-sm text-purple-100 mt-1">2 Vouchers Ready</p>
        </button>
      </div>
    </div>
  );}