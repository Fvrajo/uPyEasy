#
# Copyright (c) dushin.net  All Rights Reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of dushin.net nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY dushin.net ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL dushin.net BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import sys, utime, gc

class Log :
    '''
    This object encapsulates common logging operations
    '''
    
    DEBUG       = 'debug'
    INFO        = 'info'
    WARNING     = 'warning'
    ERROR       = 'error'
    
    def __init__(self, config, name = "unknown") :
        '''Constructor'''
        self._sinks     = self.load_sinks(config)
        self._levels    = config['levels']
        self._name      = config['name']
        self._config    = config
        self._hal       = None

    def debug(self, format_str, args = ()) :
        '''Send a debug log message'''
        self.log(self.DEBUG, 1, format_str, args)

    def info(self, format_str, args = ()) :
        '''Send an info log message'''
        self.log(self.INFO, 2, format_str, args)

    def warning(self, format_str, args = ()) :
        '''Send a warning log message'''
        self.log(self.WARNING, 3, format_str, args)

    def error(self, format_str, args = ()) :
        '''Send an error log message'''
        self.log(self.ERROR, 4, format_str, args)
    
    ##
    ## internal operations
    ##
    
    def load_sinks(self, config) :
        if 'sinks' in config :
            ret = {}
            self._mod = {}
            sink_configs = config['sinks']
            for name, config in sink_configs.items() :
                try :
                    sink_name = name + "_sink"
                    mod = __import__(sink_name)
                    self._mod[name] = mod
                    ret[name] = mod.Sink(config)
                    if config['level'] <= 1:
                        print("loaded sink {}".format(name))
                except Exception as e :
                    print("Error: failed to load sink {} with config {}.  Error: {}".format(name, config, e))
                    sys.print_exception(e)
            return ret
        else :
            return {}
            
    def create(self, level, format_str, args) :
        return {
            'name': self._name,
            'datetime': self.datetimestr(),
            'level': level,
            'message': format_str % args
        }
    
    def log(self, level, loglevel, format_str, args = ()) :
        if level in self._levels :
            message = self.create(level, format_str, args)
            for name, sink in self._sinks.items() :
                if 'sinks' in self._config :
                    sink_configs = self._config['sinks']
                    for logname, config in sink_configs.items() :
                        if name == logname and (config['level'] <= loglevel or config['level'] == 0):
                            self.do_log(sink, message)
                            if config['level']==0:
                                gc.collect()
                                self.do_log(sink, self.create(level, 'GC MEM Free: {:,}'.format(gc.mem_free()), args))
    
    def do_log(self, sink, message) :
        try :
            sink.log(message)
        except Exception as e :
            sys.print_exception(e)

    def datetimestr(self) :
        if self._hal:
            return self._hal.get_time()
        else:
            import sys
            if sys.platform == 'pyboard':
                year, month, day, hour, minute, second, millis, _tzinfo = utime.localtime()
                return "%d-%02d-%02dT%0f2d:%02d:%02d.%03d" % (year, month, day, hour, minute, second, millis)
            elif sys.platform == 'esp8266':
                year, month, day, hour, minute, second, millis, _tzinfo = utime.localtime()
                return "%d-%02d-%02dT%02d:%02d:%02d.%03d" % (year, month, day, hour, minute, second, millis)
            elif sys.platform[:5] == 'esp32':
                year, month, day, hour, minute, second, millis, _tzinfo = utime.localtime()
                return "%d-%02d-%02dT%02d:%02d:%02d.%03d" % (year, month, day, hour, minute, second, millis)
            else:
                year, month, day, hour, minute, second, millis, _tzinfo, dummy = utime.localtime()
                return "%d-%02d-%02dT%02d:%02d:%02d.%03d" % (year, month, day, hour, minute, second, millis)

    def reload(self, mod):
        import sys
        mod_name = mod.__name__
        del sys.modules[mod_name]
        return __import__(mod_name)

    def changehost(self, name, hostname):
        self._name = name
        if 'sinks' in self._config :
            ret = {}
            sink_configs = self._config['sinks']
            for name, config in sink_configs.items() :
                if name == "syslog" :
                    config['host'] = hostname
                    self.debug("Set syslog hostname {}".format(hostname))
                    try :
                        self._mod[name] = self.reload(self._mod[name])
                        ret[name] = self._mod[name].Sink(config)
                        self.debug("reloaded sink {}".format(name))
                    except Exception as e :
                        self.debug("Error: failed to load sink {} with config {}.  Error: {}".format(name, config, e))
                        sys.print_exception(e)
                else: ret[name] = self._mod[name].Sink(config)
            self._sinks = ret

    def changelevel(self, logname, level):
        if 'sinks' in self._config :
            sink_configs = self._config['sinks']
            for name, config in sink_configs.items() :
                if name == logname :
                    config['level'] = level

    def readlog (self):
        for name, sink in self._sinks.items() :
            if name == "log" :
                try :
                    return sink.read()
                except Exception as e :
                    print("ReadLog Error: {}".format(e))
                    sys.print_exception(e)

    def changehal(self, hal):
        self._hal = hal
        
    def exc(self, excep, message):
        self.debug("Critical exception: "+repr(excep)+" - message: "+message)
                    
def module_to_dict(mod) :
    ret = {}
    for i in dir(mod) :
        if not i.startswith('__') :
            ret[i] = getattr(mod, i)
    return ret

def merge_dict(a, b) :
    ret = a.copy()
    ret.update(b)
    return ret

def get_config() :
    defaults = {
        'name': "uPyEasy",
        'levels': [Log.DEBUG, Log.INFO, Log.WARNING, Log.ERROR],
        'sinks': {'console': sys.stderr}
    }
    try :
        import log_config
        return merge_dict(
            defaults, module_to_dict(log_config)
        )
    except Exception as e :
        sys.print_exception(e)
        return defaults
