#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/20 10:40
@Author  : alexanderwu
@File    : test_schema.py
"""
from metagpt.schema import AIMessage, Message, SystemMessage, UserMessage
from metagpt.schema import Task, Plan


def test_messages():
    test_content = 'test_message'
    msgs = [
        UserMessage(test_content),
        SystemMessage(test_content),
        AIMessage(test_content),
        Message(test_content, role='QA')
    ]
    text = str(msgs)
    roles = ['user', 'system', 'assistant', 'QA']
    assert all([i in text for i in roles])


class TestPlan:
    def test_add_tasks_ordering(self):
        plan = Plan()

        tasks = [
            Task(task_id="1", dependent_task_ids=["2", "3"], instruction="Third"),
            Task(task_id="2", instruction="First"),
            Task(task_id="3", dependent_task_ids=["2"], instruction="Second")
        ]  # 2 -> 3 -> 1
        plan.add_tasks(tasks)

        assert [task.task_id for task in plan.tasks] == ["2", "3", "1"]

    def test_add_tasks_to_existing_no_common_prefix(self):
        plan = Plan()

        tasks = [
            Task(task_id="1", dependent_task_ids=["2", "3"], instruction="Third"),
            Task(task_id="2", instruction="First"),
            Task(task_id="3", dependent_task_ids=["2"], instruction="Second", is_finished=True)
        ]  # 2 -> 3 -> 1
        plan.add_tasks(tasks)

        new_tasks = [Task(task_id="3", instruction="")]
        plan.add_tasks(new_tasks)

        assert [task.task_id for task in plan.tasks] == ["3"]
        assert not plan.tasks[0].is_finished  # must be the new unfinished task

    def test_add_tasks_to_existing_with_common_prefix(self):
        plan = Plan()

        tasks = [
            Task(task_id="1", dependent_task_ids=["2", "3"], instruction="Third"),
            Task(task_id="2", instruction="First"),
            Task(task_id="3", dependent_task_ids=["2"], instruction="Second")
        ]  # 2 -> 3 -> 1
        plan.add_tasks(tasks)
        plan.finish_current_task()  # finish 2
        plan.finish_current_task()  # finish 3

        new_tasks = [
            Task(task_id="4", dependent_task_ids=["3"], instruction="Third"),
            Task(task_id="2", instruction="First"),
            Task(task_id="3", dependent_task_ids=["2"], instruction="Second")
        ]  # 2 -> 3 -> 4, so the common prefix is 2 -> 3, and these two should be obtained from the existing tasks
        plan.add_tasks(new_tasks)

        assert [task.task_id for task in plan.tasks] == ["2", "3", "4"]
        assert plan.tasks[0].is_finished and plan.tasks[1].is_finished  # "2" and "3" should be the original finished one
        assert plan.current_task_id == "4"

    def test_current_task(self):
        plan = Plan()
        tasks = [
            Task(task_id="1", dependent_task_ids=["2"], instruction="Second"),
            Task(task_id="2", instruction="First")
        ]
        plan.add_tasks(tasks)
        assert plan.current_task.task_id == "2"

    def test_finish_task(self):
        plan = Plan()
        tasks = [
            Task(task_id="1", instruction="First"),
            Task(task_id="2", dependent_task_ids=["1"], instruction="Second")
        ]
        plan.add_tasks(tasks)
        plan.finish_current_task()
        assert plan.current_task.task_id == "2"

    def test_finished_tasks(self):
        plan = Plan()
        tasks = [
            Task(task_id="1", instruction="First"),
            Task(task_id="2", dependent_task_ids=["1"], instruction="Second")
        ]
        plan.add_tasks(tasks)
        plan.finish_current_task()
        finished_tasks = plan.get_finished_tasks()
        assert len(finished_tasks) == 1
        assert finished_tasks[0].task_id == "1"
