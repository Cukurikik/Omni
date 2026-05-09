namespace OmniFramework.Compute

module OmniDataPipeline =
    open System.Threading.Tasks

    type DataPoint = { Id: int; Value: float }

    let processData (data: DataPoint seq) =
        data
        |> Seq.filter (fun d -> d.Value > 0.0)
        |> Seq.map (fun d -> { d with Value = d.Value * 2.0 })
        |> Seq.toList

    let runPipelineAsync (input: DataPoint list) =
        task {
            let! result = Task.Run(fun () -> processData input)
            return result
        }
