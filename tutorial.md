This post is a tutorial on using GraphQL to query for information about
LessWrong and the Effective Altruism Forum. It's mostly intended for people who
have wanted to explore LW/EA Forum data but have found GraphQL intimidating
(this was the case for myself until a week ago).

# Examples

I've built a sample interface for both LessWrong and EA Forum:

- <https://lw2.issarice.com/>
- <https://eaforum.issarice.com/>

For article-reading and commenting purposes, most users will probably prefer to
use the official versions of the forums or the GreaterWrong counterparts.
However, one interesting feature of my interface is that it allows an easy
access to the queries used to generate pages.

By passing `format=queries` to any page, you can view the GraphQL queries that
were made to generate that page. For example, clicking "Queries" on the page
<https://eaforum.issarice.com/?view=top&before=2013-12-31&after=2013-01-01>
(which shows the top-scoring posts during 2013)
takes you to <https://eaforum.issarice.com/?view=top&offset=0&before=2013-12-31&after=2013-01-01&format=queries>
where you will see the following queries:

    {
      posts(input: {
        terms: {
          view: "top"
          limit: 50
          before: "2013-12-31"
          after: "2013-01-01"
        }
      }) {
        results {
          _id
          title
          slug
          pageUrl
          postedAt
          baseScore
          voteCount
          commentsCount
          user {
            username
            slug
          }
        }
      }
    }

    {
      comments(input: {
        terms: {
          view: "recentComments"
          limit: 10
        }
      }) {
        results {
          _id
          post {
            _id
            title
            slug
          }
          user {
            _id
            slug
          }
          plaintextExcerpt
          htmlHighlight
        }
      }
    }
