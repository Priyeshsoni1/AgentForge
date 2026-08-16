from agentforge.agent.graph import graph


def main():

    question = input("Enter Your Problem ?.......... ")

    result = graph.invoke({
        "messages": [
            {
                "role": "user",
                "content": question,
            }
        ]
    })

    final_message = result["messages"][-1]

    print("\nFinal Answer:")
    print(final_message.content)


if __name__ == "__main__":
    main()