using System.Reflection;
using RunnerGame.Gameplay;

// Fixtures only alter private state to isolate real collision behaviour from generated traffic.
static class Checks
{
    static int failures;
    static void Assert(bool value, string message) { if (!value) throw new Exception(message); }
    static void Test(string name, Action body) { try { body(); Console.WriteLine("PASS " + name); } catch(Exception e) { failures++; Console.WriteLine("FAIL " + name + ": " + e.Message); } }
    static List<TrackObject> Objects(RunSimulation s) => (List<TrackObject>)typeof(RunSimulation).GetField("objects", BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(s)!;
    static RunSimulation Empty() { var s = new RunSimulation(); s.Start(); Objects(s).Clear(); return s; }
    static void Add(RunSimulation s, ObjectKind kind, float z, float x=0) => Objects(s).Add(new TrackObject { Id=999, Kind=kind, Z=z, X=x });
    static void Advance(RunSimulation s, float seconds) { for(int i=0;i<(int)MathF.Round(seconds/.02f);i++) s.Step(.02f); }
    static void Set(RunSimulation s,string name,float value) => typeof(RunSimulation).GetProperty(name)!.SetValue(s,value);
    static RunSimulation Pedestrian(int seed=2026)
    {
        var constructor=typeof(RunSimulation).GetConstructor(new[]{typeof(int),typeof(bool)});
        Assert(constructor!=null,"pedestrian constructor missing");
        return (RunSimulation)constructor!.Invoke(new object[]{seed,true});
    }
    public static int Main()
    {
        Test("ready freezes and start moves",()=>{var s=new RunSimulation();s.Step(1);Assert(s.Distance==0,"ready moved");s.Start();s.Step(.02f);Assert(s.Distance>0 && s.Speed>=12,"start did not move");});
        Test("lane motion interpolates and clamps",()=>{var s=Empty();s.Move(1);s.Step(.02f);Assert(s.PlayerX>0&&s.PlayerX<2.5f,"teleported");Advance(s,.2f);Assert(MathF.Abs(s.PlayerX-2.5f)<.001f,"missed lane");s.Move(1);Advance(s,.2f);Assert(s.PlayerX==2.5f,"escaped lanes");});
        Test("jump has physical apex and lands",()=>{var s=Empty();s.Jump();Advance(s,.34f);Assert(s.PlayerY>1.39f&&s.PlayerY<=1.401f,"wrong apex");Advance(s,.38f);Assert(s.PlayerY==0,"did not land");});
        Test("duck expires and fast falls",()=>{var s=Empty();s.Jump();Advance(s,.2f);s.Duck();Advance(s,.2f);Assert(s.PlayerY==0&&s.IsDucking,"no fastfall");Advance(s,.62f);Assert(!s.IsDucking,"duck never expires");});
        Test("swept collision at speed cap",()=>{var s=Empty();Set(s,"Speed",30);Add(s,ObjectKind.Cone,-1.1f);s.Step(.1f);Assert(s.PursuitRemaining>0,"tunnelled");});
        Test("switch uses actual position",()=>{var s=Empty();Add(s,ObjectKind.Car,-2.5f);s.Move(1);s.Step(.02f);Assert(s.PursuitRemaining>0,"target lane bypassed car");});
        Test("jump clears bin only at sufficient height",()=>{var s=Empty();s.Jump();Advance(s,.3f);Add(s,ObjectKind.Bin,-.9f);s.Step(.02f);Assert(s.PursuitRemaining==0,"apex hit bin");var low=Empty();low.Jump();Add(low,ObjectKind.Bin,-.9f);low.Step(.02f);Assert(low.PursuitRemaining>0,"early jump magically cleared bin");});
        Test("duck fits barrier but hair standing hits",()=>{var s=Empty();s.Duck();Add(s,ObjectKind.HighBarrier,-.9f);s.Step(.02f);Assert(s.PursuitRemaining==0,"duck hit opening");var standing=Empty();Add(standing,ObjectKind.HighBarrier,-.9f);standing.Step(.02f);Assert(standing.PursuitRemaining>0,"standing cleared barrier");});
        Test("coins collected once for ten points",()=>{var s=Empty();Add(s,ObjectKind.Coin,-.8f);s.Step(.02f);s.Step(.02f);Assert(s.CoinCount==1&&s.Score==(int)s.Distance+10,"coin double count or wrong score");});
        Test("immunity then second hit catches",()=>{var s=Empty();Add(s,ObjectKind.Cone,-.9f);s.Step(.02f);Add(s,ObjectKind.Cone,-.9f);s.Step(.02f);Assert(s.Phase==RunPhase.Running,"no immunity");Objects(s).Clear();Advance(s,1.1f);Add(s,ObjectKind.Cone,-.9f);s.Step(.02f);Assert(s.Phase==RunPhase.Caught,"second hit not caught");});
        Test("ten clean seconds recovers",()=>{var s=Empty();Add(s,ObjectKind.Cone,-.9f);s.Step(.02f);Objects(s).Clear();for(int i=0;i<510;i++){s.Step(.02f);Objects(s).Clear();}Assert(s.PursuitRemaining==0,"pursuit did not recover");Add(s,ObjectKind.Cone,-.9f);s.Step(.02f);Assert(s.Phase==RunPhase.Running&&s.PursuitRemaining>0,"recovered hit caught");});
        Test("pause freezes all time",()=>{var s=Empty();s.Jump();s.TogglePause();s.Step(1);Assert(s.Distance==0&&s.PlayerY==0&&s.ElapsedTime==0,"paused mutation");s.TogglePause();s.Step(.02f);Assert(s.Distance>0,"resume broken");});
        Test("restart restores seeded ready world",()=>{var s=new RunSimulation(42);var before=string.Join(';',s.WorldObjects.Select(o=>$"{o.Id}:{o.Kind}:{o.X}:{o.Z}"));s.Start();Advance(s,2);s.Restart();Assert(s.Phase==RunPhase.Ready&&s.Distance==0&&before==string.Join(';',s.WorldObjects.Select(o=>$"{o.Id}:{o.Kind}:{o.X}:{o.Z}")),"restart mismatch");});
        Test("generated route changes lanes and rejects stationary camping",()=>
        {
            foreach(int seed in new[]{1,7,2026})
            {
                var preview=new RunSimulation(seed);
                Assert(preview.WorldObjects.Where(o=>o.Kind==ObjectKind.Coin).Select(o=>o.X).Distinct().Count()==3,"one lane remains permanently safe");
                foreach(int column in new[]{-1,0,1})
                {
                    var camper=new RunSimulation(seed);camper.Start();Set(camper,"Speed",30);camper.Move(column);
                    Advance(camper,40);
                    Assert(camper.Phase==RunPhase.Caught,"stationary camper survives seeded traffic");
                }
            }
        });
        Test("changing route reachable at cap including trailing coins and long vehicles",()=>
        {
            foreach(int seed in new[]{1,7,2026})
            {
                var s=new RunSimulation(seed);s.Start();Set(s,"Speed",30);
                float previousSafe=0;int previousRow=-1,rows=0;
                for(int i=0;i<6000;i++)
                {
                    // Remain in a row's safe lane until its entire 4m coin line and 2.7m van tail clear.
                    var row=s.WorldObjects.Where(o=>o.Kind!=ObjectKind.Coin&&o.Z<=4.5f).GroupBy(o=>o.Z).OrderByDescending(g=>g.Key).First();
                    float safe=new[]{-2.5f,0,2.5f}.Single(x=>!row.Any(o=>o.X==x));
                    int rowId=row.Min(o=>o.Id);
                    if(rowId!=previousRow)
                    {
                        if(previousRow>=0)Assert(MathF.Abs(safe-previousSafe)<=2.5f,"requires two-lane jump");
                        previousSafe=safe;previousRow=rowId;rows++;
                    }
                    if(MathF.Abs(s.PlayerX-safe)>.001f && MathF.Abs(s.PlayerX/2.5f-MathF.Round(s.PlayerX/2.5f))<.001f)s.Move(Math.Sign(safe-s.PlayerX));
                    s.Step(.02f);
                    Assert(s.Phase==RunPhase.Running&&s.PursuitRemaining==0,"safe route collides");
                    Assert(s.WorldObjects.Count<100&&s.WorldObjects.All(o=>o.Z<=15),"recycling broken");
                }
                Assert(rows>100&&s.CoinCount>=3*(rows-1),"route missed trailing coins or made no progress");
            }
        });
        Test("effective speed reflects impact then recovers",()=>
        {
            var s=Empty();Set(s,"Speed",30);Add(s,ObjectKind.Cone,-.9f);s.Step(.02f);
            var property=typeof(RunSimulation).GetProperty("EffectiveSpeed");
            Assert(property!=null,"effective speed missing");
            Assert(MathF.Abs((float)property!.GetValue(s)!-16.5f)<.01f,"impact speed not reflected");
            Objects(s).Clear();Advance(s,1.1f);
            Assert((float)property.GetValue(s)! == 30,"effective speed never recovers");
        });
        Test("render frame grouping leaves fixed ticks identical",()=>
        {
            var a=new RunSimulation(7);var b=new RunSimulation(7);a.Start();b.Start();
            for(int frame=0;frame<100;frame++)for(int tick=0;tick<3;tick++)a.Step(.02f);
            for(int tick=0;tick<300;tick++)b.Step(.02f);
            Assert(a.Distance==b.Distance&&a.Phase==b.Phase&&a.Score==b.Score,"grouped ticks differ");
            Assert(a.WorldObjects.Zip(b.WorldObjects).All(p=>p.First.Id==p.Second.Id&&p.First.Z==p.Second.Z&&p.First.Kind==p.Second.Kind),"seeded traffic differs");
        });
        Test("high speed crossing into occupied lane hits",()=>{var s=Empty();Set(s,"Speed",30);s.Move(1);Add(s,ObjectKind.Cone,-2.5f,1.2f);s.Step(.1f);Assert(s.PursuitRemaining>0,"lateral crossing missed");});
        Test("hit obstacle remains visible until recycled",()=>{var s=Empty();Add(s,ObjectKind.Car,-.9f);s.Step(.02f);Assert(s.PursuitRemaining>0&&Objects(s).Single().Active,"hit obstacle hidden");});
        Test("same contact cannot hit twice after immunity but distinct contact catches",()=>
        {
            var s=Empty();Set(s,"Speed",.1f);Add(s,ObjectKind.Van,-.9f);s.Step(.02f);
            Advance(s,1.1f);
            Assert(s.Phase==RunPhase.Running&&s.InvulnerabilityRemaining==0,"same obstacle hit twice");
            Add(s,ObjectKind.Cone,-.9f);s.Step(.02f);
            Assert(s.Phase==RunPhase.Caught,"distinct obstacle ignored");
        });
        Test("pedestrian rows replace traffic while preserving classic seeded layout",()=>
        {
            foreach(int seed in new[]{1,7,2026})
            {
                var classic=new RunSimulation(seed);var pedestrian=Pedestrian(seed);
                Assert(pedestrian.WorldObjects.Any(o=>o.Kind.ToString()=="Planter"),"no planter generated");
                Assert(pedestrian.WorldObjects.All(o=>o.Kind is not (ObjectKind.Car or ObjectKind.Van or ObjectKind.Pothole)),"road traffic remains");
                Assert(classic.WorldObjects.Zip(pedestrian.WorldObjects).All(p=>
                    p.First.Id==p.Second.Id&&MathF.Abs(p.First.X/2.5f-p.Second.X/1.5f)<.001f&&p.First.Z==p.Second.Z&&
                    p.Second.Kind.ToString()==(p.First.Kind is ObjectKind.Car or ObjectKind.Van ? "Planter" : p.First.Kind==ObjectKind.Pothole ? "Cone" : p.First.Kind.ToString())),"profile changed random sequence or route");
                string before=string.Join(';',pedestrian.WorldObjects.Select(o=>$"{o.Id}:{o.Kind}:{o.X}:{o.Z}"));
                pedestrian.Start();Advance(pedestrian,2);pedestrian.Restart();
                Assert(before==string.Join(';',pedestrian.WorldObjects.Select(o=>$"{o.Id}:{o.Kind}:{o.X}:{o.Z}")),"pedestrian restart differs");
            }
        });
        Test("pedestrian paths fit three metre centre span and movement targets",()=>
        {
            var s=Pedestrian();
            Assert(s.WorldObjects.Select(o=>o.X).Distinct().Order().SequenceEqual(new[]{-1.5f,0,1.5f}),"pedestrian path centres exceed strip");
            s.Start();Objects(s).Clear();s.Move(1);Advance(s,.2f);
            Assert(MathF.Abs(s.PlayerX-1.5f)<.001f,"pedestrian movement targets road lane");
            s.Move(-1);Advance(s,.2f);Assert(MathF.Abs(s.PlayerX)<.001f,"pedestrian cannot return to centre");
        });
        Test("planter uses physical footprint and jump clearance",()=>
        {
            Assert(Enum.TryParse<ObjectKind>("Planter",out var planter),"planter kind missing");
            foreach(var fixture in new[]{(x:.75f,z:0f,hit:true),(x:.78f,z:0f,hit:false),(x:0f,z:1.25f,hit:true),(x:0f,z:1.28f,hit:false)})
            {
                var s=Empty();Add(s,planter,fixture.z,fixture.x);s.Step(.002f);
                Assert((s.PursuitRemaining>0)==fixture.hit,"planter footprint differs from .925m square");
            }
            foreach(var fixture in new[]{(height:1.27f,hit:true),(height:1.29f,hit:false)})
            {
                var s=Empty();Set(s,"PlayerY",fixture.height);Add(s,planter,0);s.Step(.002f);
                Assert((s.PursuitRemaining>0)==fixture.hit,"planter top differs from 1.279m");
            }
            var jumping=Empty();jumping.Jump();Advance(jumping,.3f);Add(jumping,planter,0);jumping.Step(.02f);
            Assert(jumping.PursuitRemaining==0,"jump apex cannot clear planter");
        });
        Test("pedestrian three lane route remains reachable at speed cap",()=>
        {
            foreach(int seed in new[]{1,7,2026})
            {
                var s=Pedestrian(seed);s.Start();Set(s,"Speed",30);int rows=0,last=-1;
                for(int i=0;i<6000;i++)
                {
                    Assert(s.WorldObjects.All(o=>o.Kind is not (ObjectKind.Car or ObjectKind.Van or ObjectKind.Pothole)),"generated road traffic later");
                    var row=s.WorldObjects.Where(o=>o.Kind!=ObjectKind.Coin&&o.Z<=4.5f).GroupBy(o=>o.Z).OrderByDescending(g=>g.Key).First();
                    float safe=new[]{-s.LaneSpacing,0,s.LaneSpacing}.Single(x=>!row.Any(o=>o.X==x));
                    int id=row.Min(o=>o.Id);if(id!=last){last=id;rows++;}
                    if(MathF.Abs(s.PlayerX-safe)>.001f&&MathF.Abs(s.PlayerX/s.LaneSpacing-MathF.Round(s.PlayerX/s.LaneSpacing))<.001f)s.Move(Math.Sign(safe-s.PlayerX));
                    s.Step(.02f);Assert(s.Phase==RunPhase.Running&&s.PursuitRemaining==0,"pedestrian route collides");
                }
                Assert(rows>100&&s.CoinCount>=3*(rows-1),"pedestrian route misses trailing coins");
            }
        });
        return failures==0?0:1;
    }
}
