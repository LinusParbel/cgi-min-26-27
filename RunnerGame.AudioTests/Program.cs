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
run.PrepareVanCrashPreview();while(run.VanCrash==null)run.Step(.02f);audio.Update(run);run.Step(6);audio.Update(run);
Check(float.IsNaN(audio.PlaybackTime),"Completion left audio playing");
using var muted=new VanCrashAudio(path,true);run.PrepareVanCrashPreview();while(run.VanCrash==null)run.Step(.02f);muted.Update(run);
Check(float.IsNaN(muted.PlaybackTime),"Mute opened the audio device");
Console.WriteLine("PASS native scene audio: seek, pause, resume, restart, completion and mute");
