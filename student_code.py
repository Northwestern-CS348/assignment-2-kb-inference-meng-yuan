import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Student code goes here
        # if a rule

        if isinstance(fact_or_rule, Rule):
            fact_or_rule = self._get_rule(fact_or_rule)
            if fact_or_rule.asserted:
                return
            else:
                if fact_or_rule in self.rules:
                    fact_or_rule = self._get_rule(fact_or_rule)
                    if fact_or_rule.supports_facts == [] and fact_or_rule.supports_rules == [] and fact_or_rule.supported_by == []:
                        self.rules.remove(fact_or_rule)
                    else:
                        self.kb_adjust(fact_or_rule)

        # if a fact
        else:
            fact_or_rule = self._get_fact(fact_or_rule)
            # if asserted adjust supports_fact & support_rule first then remove
            if not fact_or_rule.asserted:
                return
            else:
                if fact_or_rule in self.facts:
                    fact_or_rule = self._get_fact(fact_or_rule)
                    if fact_or_rule.supports_rules == [] and fact_or_rule.supports_facts == [] and fact_or_rule.supported_by == []:
                        self.facts.remove(fact_or_rule)
                    else:
                        self.kb_adjust(fact_or_rule)




    def kb_retract2(self,fact_or_rule):

        # if asserted
        if fact_or_rule.asserted:
            return
        else:
            self.kb_adjust(fact_or_rule)




    def kb_adjust(self,f_o_r):

        # adjust supported_by
        # if f_o_r is a fact
        if isinstance(f_o_r, Fact):
            f_o_r = self._get_fact(f_o_r)
            a = 0
            for i in range(0, len(f_o_r.supported_by)):
                    x1 = self._get_rule(f_o_r.supported_by[i][1])
                    x2 = self._get_fact(f_o_r.supported_by[i][0])
                    x1.supports_facts.remove(f_o_r)
                    x2.supports_facts.remove(f_o_r)
            #self.facts.remove(f_o_r)
        # if f_o_r is a rule
        else:
            f_o_r = self._get_rule(f_o_r)
            a = 1
            for i in range(0, len(f_o_r.supported_by)):
                    x1 = self._get_rule(f_o_r.supported_by[i][1])
                    x2 = self._get_fact(f_o_r.supported_by[i][0])
                    x1.supports_rules.remove(f_o_r)
                    x2.supports_rules.remove(f_o_r)
            #self.rules.remove(f_o_r)


        # adjust supports_facts
        for fact in f_o_r.supports_facts:
            fact = self._get_fact(fact)
            delete = []
            for i in range(0, len(fact.supported_by)):

                if fact.supported_by[i][a] == f_o_r:
                    delete.append(fact.supported_by[i])
            fact.supported_by = [x for x in fact.supported_by if x not in delete]
            if fact.supported_by == []:
                self.kb_retract2(fact)


        # adjust supports_rules
        for rule in f_o_r.supports_rules:
            rule = self._get_rule(rule)
            delete = []
            for i in range(0, len(rule.supported_by)):

                if rule.supported_by[i][a] == f_o_r:
                    delete.append(rule.supported_by[i])
            rule.supported_by = [x for x in rule.supported_by if x not in delete]
            if rule.supported_by == []:
                self.kb_retract2(rule)

        if isinstance(f_o_r, Fact):
            f_o_r = self._get_fact(f_o_r)
            self.facts.remove(f_o_r)
        else:
            f_o_r = self._get_rule(f_o_r)
            self.rules.remove(f_o_r)





class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing            
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Student code goes here
        b = match( fact.statement,rule.lhs[0])
        if b == False:
            return
        if len(rule.lhs) == 0:
            return
        if len(rule.lhs) == 1:
            newfact = Fact(instantiate(rule.rhs, b), [[fact,rule]])
            #print newfact
            rule.supports_facts.append(newfact)
            fact.supports_facts.append(newfact)
            kb.kb_add(newfact)
            #newfact.supported_by.append([fact,rule])

        #more than one lhs
        else:
            locallhs = []
            localrule = []
            for i in range(1, len(rule.lhs)):
                locallhs.append(instantiate(rule.lhs[i], b))
            localrule.append(locallhs)
            localrule.append(instantiate(rule.rhs, b))
            newrule = Rule(localrule,[[fact, rule]])
            rule.supports_rules.append(newrule)
            fact.supports_rules.append(newrule)
            kb.kb_add(newrule)
            #newrule.supported_by.append([fact,rule])


