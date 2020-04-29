using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using Microsoft.ML;
using Microsoft.Extensions.ML;
using DataRobot.Model.DataModels;
using System.Reflection;

namespace WebServer.Controllers
{

    [Route("/predict/")]
    public class PredictionController : Controller
    {

        public static string positiveClassLabel = "";
        public static string negativeClassLabel = "";

        public  readonly PredictionEngine<ModelInput, ModelOutput> predEngine;
        private readonly object _predictionEngineLock = new object();

        public  readonly PredictionEnginePool<ModelInput, ModelOutput> predEnginePool;
        
        public PredictionController(PredictionEngine<ModelInput, ModelOutput> predictionEngine)
        {

            predEngine = predictionEngine;
            
        }

        [HttpPost]
        public Task<string> Predict(HttpContext context)
        {
            
            List<ModelInput> scoringdata = new List <ModelInput>();

            // we take the first/only file
            var f = context.Request.Form.Files.First();
            if (f.Length == 0)
            {
                return  Task.FromResult("No scoring data"); 
            }
            
            System.Text.Encoding encoding = System.Text.Encoding.UTF8;
            System.IO.StreamReader reader = new System.IO.StreamReader(f.OpenReadStream(), encoding);

            string[] result = reader.ReadToEnd().Split(Environment.NewLine.ToCharArray(), StringSplitOptions.RemoveEmptyEntries);
            reader.Close();
            scoringdata = ConvertCsvToScoringRows(result);
            

            foreach (var formField in context.Request.Form)
            {
                // Form data 
                if (formField.Key == "positiveClassLabel"){
                    positiveClassLabel = formField.Value;
                }
                if (formField.Key == "negativeClassLabel"){
                    negativeClassLabel = formField.Value;
                }
               
            }
            
            var txtRp = "{\"predictions\":[";
            foreach (ModelInput row in scoringdata)
            {
                                
                // score records                    
                    ModelOutput modelOutput = predEngine.Predict(row);
                    
                    if (txtRp != "{\"predictions\":["){
                        txtRp = txtRp + ",";
                    }
                    
                    // if labels were passed we use those, if not, we assume it is regression.
                    if (positiveClassLabel != ""){
                        // we return the Label, since DR expects that for binary classificationn the sum adds up to 1
                        if (modelOutput.Prediction == false){    
                            txtRp =  txtRp + "{\"" + positiveClassLabel + "\": 0.0" + ", \"" + negativeClassLabel + "\": 1.0}";
                        }
                        else {   
                            txtRp =  txtRp + "{\"" + positiveClassLabel + "\": 1.0" + ", \"" + negativeClassLabel + "\": 0.0}";
                        }
                    }
                    else{
                        // regression
                        //{"predictions": [0, 1, 2, 3, 4]}
                        txtRp =  txtRp  + modelOutput.Score ;
                    }

            }
            txtRp = txtRp + "]}";
 
            return Task.FromResult(txtRp);
            
        }

        public static List<ModelInput> ConvertCsvToScoringRows(string[] lines) 
        {

            PropertyInfo[] properties = typeof(ModelInput).GetProperties();
            Type ModelInputType = typeof(ModelInput);
            var listScoringRows = new List <ModelInput>();

            var csv = new List<string[]>();
            foreach (string line in lines)
                csv.Add(line.Split(','));

            for (int i = 1; i < lines.Length; i++)
            {
                
                ModelInput scoringRow = new ModelInput();
                int j = 0;
                foreach (PropertyInfo property in properties)
                {
                    try{
                        // ensure feature name matches feature name that the model expects
                        string name = property.Name;

                        // Map property value.
                        PropertyInfo piScoringRow = ModelInputType.GetProperty(name);

                        // Current value from CSV
                        var value = csv[i][j];
                        // ensure that feature data type matches what model is expecting
                        string type = property.PropertyType.Name;
                        dynamic new_value = dynamic_cast(value, type);
    
                        piScoringRow.SetValue(scoringRow, new_value);
                        j++;
                        
                    }
                    catch(Exception ex)
                    {
                        // fail sillently and add missing values
                        Console.WriteLine(ex.Message);
                        string name = property.Name;
                        PropertyInfo piScoringRow = ModelInputType.GetProperty(name);
                        string type = property.PropertyType.Name;
                        // use defautl value for missing values
                        var value = "0";
                        dynamic new_value = dynamic_cast(value, type);
                        piScoringRow.SetValue(scoringRow, new_value);
                        j++;
                        Console.WriteLine(type + " - " + name + ":" + new_value);
                        
                    }
                    
                }
                listScoringRows.Add(scoringRow);
                
            }

            return listScoringRows; 
        }
        public static dynamic dynamic_cast(string value, string type){
            // you might want to add more types, depending on you your model type

                switch (type)
                {
                    case "Single":
                        dynamic new_value = value.Replace("\"","");
                        if (new_value.Length == 0){
                            new_value = 0;
                        }
                        else {
                            try{
                                new_value = System.Convert.ToSingle(new_value);
                            }
                             catch (System.FormatException err){
                                new_value = 0;
                                Console.WriteLine(err.Message);
                                return new_value;
                            }
                        }
                        return new_value;
                            
                    case "Boolean":
                        dynamic new_bool_value = value.Replace("\"","").Replace("0","False").Replace("1","True");
                        if (new_bool_value.Length == 0){
                            new_bool_value = 0;
                        }
                        else {
                            try {
                                new_bool_value = System.Convert.ToBoolean(new_bool_value);
                            
                            }
                             catch (System.FormatException err){
                                new_bool_value = System.Convert.ToBoolean("False");
                                Console.WriteLine(err.Message);
                                return new_bool_value;
                            }
                        }
                        return new_bool_value;
            
                    default:
                        return System.Convert.ToString(value.Replace("\"", ""));     
                
                }
        }
    }
}
