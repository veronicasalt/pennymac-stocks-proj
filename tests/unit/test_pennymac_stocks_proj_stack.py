import aws_cdk as core
import aws_cdk.assertions as assertions

from pennymac_stocks_proj.pennymac_stocks_proj_stack import PennymacStocksProjStack

# example tests. To run these tests, uncomment this file along with the example
# resource in pennymac_stocks_proj/pennymac_stocks_proj_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = PennymacStocksProjStack(app, "pennymac-stocks-proj")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
