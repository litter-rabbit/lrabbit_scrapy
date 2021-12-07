from lrabbit_scrapy.asynico_basespider import BaseSpider
import sqlalchemy as sa


class Spider(BaseSpider):
    # setup
    is_open_mysql = False
    is_drop_tables = False
    # reset all tasks,files,this is may delete all data files
    reset_task_list = False

    """
        not call a method or attribute start_with of 'file','table'
    """
    # datastore
    table_table1 = [
        sa.Column('val', sa.String(255)),
    ]

    # file_store
    file_blogPost = [
        'id', 'title', 'datetime', 'content'
    ]

    def __init__(self, spider_name):
        super(Spider, self).__init__(spider_name)

    async def worker(self, task):
        """

        code your worker method

        :param task:
        :return:
        """
        """
         mysql work method
        """
        # await self.insert_one(self.tables['table1'].insert().values(val=str(task)))
        # res = await self.query(self.tables['table1'].select())
        # res = await res.fetchall()

        """
         want to see how to work,uncomment beyond code
        """
        url = f"http://www.lrabbit.life/post_detail/?id={task}"

        data = {"id": task, "datetime": "1997", "title": "lrabbit", "content": "hello"}
        if data:
            self.all_files['blogPost'].write(data)

    async def create_tasks(self):
        return [i for i in range(100)]


if __name__ == '__main__':
    s = Spider(__file__)
    s.run()
