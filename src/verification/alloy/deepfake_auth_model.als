sig User {
  clearance: ClearanceLevel
}

abstract sig ClearanceLevel {}
one sig Admin, Standard extends ClearanceLevel {}

sig DeepfakeLog {
  accessedBy: User
}

fact SecureAccess {
  all log: DeepfakeLog | log.accessedBy.clearance = Admin
}

assert NoUnauthorizedAccess {
  no log: DeepfakeLog | log.accessedBy.clearance = Standard
}

check NoUnauthorizedAccess
