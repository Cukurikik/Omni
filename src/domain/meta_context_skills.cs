using System;
using Omni.Domain.Monads;

namespace Omni.Business.MetaContext
{
    public class SkillEvolution
    {
        public Result<bool, Exception> UpgradeSkill(string skill)
        {
            if (string.IsNullOrEmpty(skill)) return Result<bool, Exception>.Err(new Exception("Skill missing"));
            return Result<bool, Exception>.Ok(true);
        }
    }
}
