package omni.medical

class PatientView {
    fun render(patientId: String): Result<String> {
        if (patientId.isBlank()) return Result.failure(Exception("ID required"))
        return Result.success("Patient Record $patientId rendered securely")
    }
}
