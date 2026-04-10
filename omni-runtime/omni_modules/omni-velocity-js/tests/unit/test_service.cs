// Unit test: DomainService Execute/Query
using Xunit;
namespace Omni.omni_velocity_js.Tests {
    public class ServiceTests {
        [Fact] public void Execute_ValidCommand_ReturnsSuccess() {
            var repo = new InMemoryRepository();
            var svc = new DomainService(repo, new SchemaValidator(), new InMemoryEventBus());
        }
    }
}