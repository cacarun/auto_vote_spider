from scrapy import cmdline

name = 'vote'
cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())


