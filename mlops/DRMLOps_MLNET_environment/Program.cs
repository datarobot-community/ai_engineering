using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Hosting;
using System.Threading;


namespace WebServer
{
    public class Program
    {
        
        private static CancellationTokenSource cts = new CancellationTokenSource();
        private static string[] _args;
        private static bool _restartRequest;

        public static async Task Main(string[] args)
        {
            _args = args;

            await StartServer();
            while (_restartRequest)
            {
                _restartRequest = false;
                Console.WriteLine("Restarting App");
                await StartServer();
            }
        }
        public static void Restart()
        {
            
            _restartRequest = true;
            cts.Cancel();
        }

        private static async Task StartServer()
        {
            try
            {
                cts = new CancellationTokenSource();
                await CreateHostBuilder(_args).RunConsoleAsync(cts.Token);
            }
            catch (OperationCanceledException e)
            {
                Console.WriteLine(e);
            }
        }

        public static IHostBuilder CreateHostBuilder(string[] args) =>
            Host.CreateDefaultBuilder(args)
                .ConfigureWebHostDefaults(webBuilder =>
                {
                    webBuilder.UseStartup<Startup>();
                });
        
        
    }
}
