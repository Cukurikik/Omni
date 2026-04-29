# OMNI EduGenius Domain Engine — Domain Layer
# Absorbing Irash-Perera/EduGenius pipeline patterns for O/Level Mathematics
# Ruby domain model mapping student profiles to adaptive tutoring tracks.

class OmniEduGeniusDomain
  MATH_TOPICS = %w[algebra geometry statistics arithmetic calculus].freeze
  DIFFICULTY = %w[beginner intermediate advanced].freeze

  def initialize
    @students = {}
    @tutoring_sessions = 0
  end

  def register_student(id, name, initial_assessment = {})
    return { ok: false, error: "EduError: Invalid ID or name" } if id.nil? || name.nil?

    profile = {
      name: name,
      topic_mastery: MATH_TOPICS.each_with_object({}) { |t, h| h[t] = initial_assessment[t] || "beginner" },
      sessions_completed: 0
    }
    @students[id] = profile
    { ok: true, student_id: id }
  end

  def plan_next_session(student_id, target_topic)
    return { ok: false, error: "EduError: Student not found" } unless @students.key?(student_id)
    return { ok: false, error: "EduError: Invalid topic" } unless MATH_TOPICS.include?(target_topic)

    student = @students[student_id]
    current_difficulty = student[:topic_mastery][target_topic]

    @tutoring_sessions += 1
    session_plan = {
      topic: target_topic,
      difficulty: current_difficulty,
      generated_nodes: generate_curriculum_nodes(target_topic, current_difficulty),
      session_id: "session-#{Time.now.to_i}-#{@tutoring_sessions}"
    }

    { ok: true, plan: session_plan }
  end

  def report_session_result(student_id, target_topic, passed)
    return { ok: false, error: "EduError: Student not found" } unless @students.key?(student_id)
    return { ok: false, error: "EduError: Invalid topic" } unless MATH_TOPICS.include?(target_topic)

    student = @students[student_id]
    current = student[:topic_mastery][target_topic]
    
    if passed
      idx = DIFFICULTY.index(current)
      student[:topic_mastery][target_topic] = DIFFICULTY[idx + 1] if idx < DIFFICULTY.size - 1
    end
    
    student[:sessions_completed] += 1
    { ok: true, new_level: student[:topic_mastery][target_topic] }
  end

  def diagnostics
    {
      engine: "OmniEduGeniusDomain",
      registered_students: @students.size,
      sessions_planned: @tutoring_sessions,
      status: "Operational"
    }
  end

  private

  def generate_curriculum_nodes(topic, difficulty)
    case topic
    when "algebra"
      difficulty == "beginner" ? ["Variables", "Simple Equations"] : ["Polynomials", "Quadratics"]
    when "geometry"
      difficulty == "beginner" ? ["Angles", "Shapes"] : ["Trigonometry", "Theorems"]
    else
      ["Core concepts", "Practice Problem Set"]
    end
  end
end
