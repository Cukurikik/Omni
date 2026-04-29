# OMNI KUBEFLOW: Pipeline Manifest Compiler
# Ruby-based DSL translation to Argo YAML for Kubernetes pipeline execution.
# Source: kubeflow/pipelines

require 'yaml'

module Omni
  module Kubeflow
    class CompileError < StandardError; end

    class PipelineCompiler
      def initialize(pipeline_name)
        @pipeline_name = pipeline_name
        @tasks = []
      end

      # Adds a container execution task to the DAG
      def add_task(name, image, command, args, dependencies = [])
        @tasks << {
          name: name,
          template: "#{name}-tmpl",
          dependencies: dependencies,
          image: image,
          command: command,
          args: args
        }
      end

      # Compiles the DAG into an Argo Workflow YAML structure
      def compile
        raise CompileError, "No tasks defined" if @tasks.empty?

        dag_tasks = @tasks.map do |task|
          t = { "name" => task[:name], "template" => task[:template] }
          t["dependencies"] = task[:dependencies] unless task[:dependencies].empty?
          t
        end

        templates = [{
          "name" => "main-dag",
          "dag" => { "tasks" => dag_tasks }
        }]

        @tasks.each do |task|
          templates << {
            "name" => task[:template],
            "container" => {
              "image" => task[:image],
              "command" => task[:command],
              "args" => task[:args]
            }
          }
        end

        workflow = {
          "apiVersion" => "argoproj.io/v1alpha1",
          "kind" => "Workflow",
          "metadata" => { "generateName" => "#{@pipeline_name}-" },
          "spec" => {
            "entrypoint" => "main-dag",
            "templates" => templates
          }
        }

        workflow.to_yaml
      end
    end
  end
end

# Usage:
# compiler = Omni::Kubeflow::PipelineCompiler.new("model-training")
# compiler.add_task("preprocess", "python:3.9", ["python"], ["preprocess.py"])
# compiler.add_task("train", "tensorflow/tensorflow:latest-gpu", ["python"], ["train.py"], ["preprocess"])
# yaml_output = compiler.compile
