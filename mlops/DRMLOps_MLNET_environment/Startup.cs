using System;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.AspNetCore.Http;

using Microsoft.ML;
using System.IO;
using DataRobot.Model.DataModels;


namespace WebServer
{
    public class Startup
    {
        Controllers.PredictionController prediction;
        private string modelPath;
        PredictionEngine<ModelInput, ModelOutput> predictionEngine;

        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
            modelPath = Path.Combine("MLModel.zip");
        }

        public IConfiguration Configuration { get; }

        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
            
            // Initialize MLContext
            MLContext ctx = new MLContext();
            
            //Load model
            DataViewSchema modelInputSchema;
            ITransformer mlModel = ctx.Model.Load(modelPath, out modelInputSchema);
            
            // Create prediction engine & pass it to our controller
            predictionEngine  = ctx.Model.CreatePredictionEngine<ModelInput,ModelOutput>(mlModel);

            Console.WriteLine(modelInputSchema.ToString());
            

            prediction = new Controllers.PredictionController(predictionEngine);

            Console.WriteLine("Prediction Engine initialized successfully");
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            

            app.UseRouting();

           
            app.Use(next => async context =>
            {
                
                var pathend = context.Request.Path.ToString();
            
                // needs dynamic path handling because DR uses a prefix
                if (pathend.Contains("predict") == false)
                {
                    // return status
                    await context.Response.WriteAsync("Server is running Startup");
                    return;
                }
                if (pathend.Contains("predict")){
                    // call predictions
                    string result = await prediction.Predict(context);
                    await context.Response.WriteAsync(result);
                    
                    return;
                } 

                await next(context);
            });
        }
    }
}