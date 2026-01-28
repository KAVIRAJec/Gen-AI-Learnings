"""
Test Cases for Agent Evaluation with Reference Trajectories
"""

TEST_CASES = [
    {
        "query": "What is artificial intelligence?",
        "expected_tool": "Web_Search",
        "ground_truth": "artificial intelligence technology computers simulate human intelligence learning reasoning",
        "reference_trajectory": [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "Web_Search",
                            "arguments": '{"query": "What is artificial intelligence definition and explanation"}'
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "Web_Search",
                "content": "Search results about artificial intelligence from IBM, Google Cloud, Wikipedia"
            },
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "Web_Search",
                            "arguments": '{"query": "What is artificial intelligence AI definition and explanation modern"}'
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "Web_Search",
                "content": "AI is technology that enables computers to simulate human intelligence, learning, reasoning, decision making"
            },
            {
                "role": "assistant",
                "content": "Artificial Intelligence (AI) is a technology that enables computers and machines to simulate human intelligence and perform tasks that typically require human cognitive abilities including learning, reasoning, problem solving, and decision making."
            }
        ]
    },
    {
        "query": "What is the company's vacation policy?",
        "expected_tool": "Document_Search",
        "ground_truth": "vacation policy leave casual sick privilege annual time off",
        "reference_trajectory": [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "Document_Search",
                            "arguments": '{"query": "vacation policy employee time off"}'
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "Document_Search",
                "content": "Retrieved compensatory time off, bereavement leave, sabbatical leave information from HR_Policy.pdf"
            },
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "Document_Search",
                            "arguments": '{"query": "annual leave PTO paid time off policy"}'
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "Document_Search",
                "content": "Retrieved complete leave policy including Casual Leave (12 days), Sick Leave (12 days), Privilege Leave (12 days after 12 months) from HR_Policy.pdf"
            },
            {
                "role": "assistant",
                "content": "The company's vacation policy includes Casual Leave (12 days), Sick Leave (12 days), Privilege Leave (12 days after 12 months, can accumulate to 45 days), plus Bereavement Leave, Maternity/Paternity Leave, Sabbatical Leave, and Compensatory Time Off."
            }
        ]
    },
    # {
    #     "query": "What health benefits does the company offer?",
    #     "expected_tool": "Document_Search",
    #     "ground_truth": "health insurance benefits medical coverage employee dependents",
    #     "reference_trajectory": [
    #         {
    #             "role": "assistant",
    #             "tool_calls": [
    #                 {
    #                     "type": "function",
    #                     "function": {
    #                         "name": "Document_Search",
    #                         "arguments": '{"query": "company health benefits insurance coverage employee benefits"}'
    #                     }
    #                 }
    #             ]
    #         },
    #         {
    #             "role": "tool",
    #             "name": "Document_Search",
    #             "content": "Retrieved health insurance for employees and dependents"
    #         },
    #         {
    #             "role": "assistant",
    #             "content": "The company offers comprehensive health insurance"
    #         }
    #     ]
    # },
    {
        "query": "What are the company's core values and how many employees does it have?",
        "expected_tool": "Document_Search",
        "ground_truth": "core values excellence one presidio forward-thinking accountability 3500 employees",
        "reference_trajectory": [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "Document_Search",
                            "arguments": '{"query": "company core values number of employees"}'
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "Document_Search",
                "content": "Retrieved partial information about Excellence core value from HR_Policy.pdf"
            },
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "Document_Search",
                            "arguments": '{"query": "Presidio core values complete list total number of employees"}'
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "Document_Search",
                "content": "Retrieved salary policy and employee benefits but not complete core values or employee count"
            },
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "Document_Search",
                            "arguments": '{"query": "Presidio core values excellence mission statement"}'
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "Document_Search",
                "content": "Retrieved complete core values (Excellence, One Presidio, Forward-Thinking, Accountability) and company stats: 3,500 employees, 6,600+ customers, 40+ global locations from HR_Policy.pdf"
            },
            {
                "role": "assistant",
                "content": "Presidio has approximately 3,500 employees across 40+ global locations. The company's core values are: Excellence (passionate and relentless in delivering solutions), One Presidio (unified global team valuing diversity), Forward-Thinking (creative innovators anticipating future needs), and Accountability."
            }
        ]
    }
    # {
    #     "query": "What are the latest developments in generative AI?",
    #     "expected_tool": "Web_Search",
    #     "ground_truth": "generative AI developments video generation",
    #     "reference_trajectory": [
    #         {
    #             "role": "assistant",
    #             "tool_calls": [
    #                 {
    #                     "type": "function",
    #                     "function": {
    #                         "name": "Web_Search",
    #                         "arguments": '{"query": "latest developments generative AI 2024"}'
    #                     }
    #                 }
    #             ]
    #         },
    #         {
    #             "role": "tool",
    #             "name": "Web_Search",
    #             "content": "Retrieved AI developments"
    #         },
    #         {
    #             "role": "assistant",
    #             "content": "Latest developments in generative AI"
    #         }
    #     ]
]
    # {
    #     "query": "What is the company culture and work environment like?",
    #     "expected_tool": "Document_Search",
    #     "ground_truth": "company culture inclusive collaborative",
    #     "reference_trajectory": [
    #         {
    #             "role": "assistant",
    #             "tool_calls": [
    #                 {
    #                     "type": "function",
    #                     "function": {
    #                         "name": "Document_Search",
    #                         "arguments": '{"query": "company culture work environment values"}'
    #                     }
    #                 }
    #             ]
    #         },
    #         {
    #             "role": "tool",
    #             "name": "Document_Search",
    #             "content": "Retrieved company culture information"
    #         },
    #         {
    #             "role": "assistant",
    #             "content": "The company culture is professional and inclusive"
    #         }
    #     ]
    # }
