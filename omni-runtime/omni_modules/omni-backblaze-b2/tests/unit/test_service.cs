// Unit test: DomainService Execute/Query
using Xunit;
namespace Omni.omni_backblaze_b2.Tests {
    public class ServiceTests {
        [Fact] public void Execute_ValidCommand_ReturnsSuccess() {
            var repo = new InMemoryRepository();
            var svc = new DomainService(repo, new SchemaValidator(), new InMemoryEventBus());
        }
    }
}