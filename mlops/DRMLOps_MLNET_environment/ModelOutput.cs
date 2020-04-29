using Microsoft.ML.Data;

namespace DataRobot.Model.DataModels
{
    public class ModelOutput
    {
        [ColumnName("PredictedLabel")]
        public bool Prediction { get; set; }

        public float Score { get; set; }

    }
}