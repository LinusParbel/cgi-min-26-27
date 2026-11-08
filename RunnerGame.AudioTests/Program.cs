using RunnerGame.Audio;
using RunnerGame.Gameplay;

string path=args.Length>0?args[0]:Path.Combine("RunnerGame","Assets","Animations","VanCrash","crash.wav");
static void Check(bool value,string message){if(!value)throw new Exception(message);}
using var audio=new VanCrashAudio(path,false);
var run=new RunSimulation();run.PrepareVanCrashPreview();while(run.VanCrash==null)run.Step(.02f);
audio.Update(run);
Check(float.IsFinite(audio.PlaybackTime),"No waveOut device: native audio checks cannot pass");
run.Step(1.2f);audio.Update(run);
Check(Math.Abs(audio.PlaybackTime-1.2f)<.075f,"Audio failed to seek to scene after a clock discontinuity");
run.TogglePause();audio.Update(run);Thread.Sleep(80);float before=audio.PlaybackTime;Thread.Sleep(100);
Check(Math.Abs(audio.PlaybackTime-before)<.025f,"Paused audio advanced");
run.TogglePause();audio.Update(run);Thread.Sleep(100);
Check(audio.PlaybackTime>before+.04f,"Resumed audio stayed paused");
run.Restart();audio.Update(run);Check(float.IsNaN(audio.PlaybackTime),"Restart left audio playing");
run.PrepareVanCrashPreview();while(run.VanCrash==null)run.Step(.02f);audio.Update(run);
run.Step(8.2f);audio.Update(run);Check(Math.Abs(audio.PlaybackTime-8.2f)<.075f,"Late ticket audio seek failed");
run.TogglePause();audio.Update(run);Thread.Sleep(80);float ticketPaused=audio.PlaybackTime;Thread.Sleep(100);
Check(Math.Abs(audio.PlaybackTime-ticketPaused)<.025f,"Ticket flutter audio continued during pause");
run.TogglePause();audio.Update(run);run.Step(11);audio.Update(run);
Check(float.IsNaN(audio.PlaybackTime),"Completion left audio playing");
using var muted=new VanCrashAudio(path,true);run.PrepareVanCrashPreview();while(run.VanCrash==null)run.Step(.02f);muted.Update(run);
Check(float.IsNaN(muted.PlaybackTime),"Mute opened the audio device");
Console.WriteLine("PASS native scene audio: seek, pause, resume, restart, completion and mute");

using var coneAudio=new VanCrashAudio(Path.Combine("RunnerGame","Assets","Animations","ConeCrash","crash.wav"),false,1,ConeCrashState.Duration);
run.PrepareConeCrashPreview();while(run.ConeCrash==null)run.Step(.02f);coneAudio.UpdateCone(run);
Check(float.IsFinite(coneAudio.PlaybackTime),"Cone audio device did not start");
run.Step(8.4f);coneAudio.UpdateCone(run);Check(Math.Abs(coneAudio.PlaybackTime-8.4f)<.075f,"Cone ticket seek failed");
run.TogglePause();coneAudio.UpdateCone(run);Thread.Sleep(80);float conePaused=coneAudio.PlaybackTime;Thread.Sleep(100);
Check(Math.Abs(coneAudio.PlaybackTime-conePaused)<.025f,"Cone pause advanced");
run.TogglePause();coneAudio.UpdateCone(run);Thread.Sleep(100);Check(coneAudio.PlaybackTime>conePaused+.04f,"Cone resume failed");
run.Step(9);coneAudio.UpdateCone(run);Check(float.IsNaN(coneAudio.PlaybackTime),"Cone completion left audio playing");
run.Restart();coneAudio.UpdateCone(run);Check(float.IsNaN(coneAudio.PlaybackTime),"Cone reset left audio playing");
Console.WriteLine("PASS native cone audio: 17-second mix, late ticket seek, pause, resume, completion and reset");
